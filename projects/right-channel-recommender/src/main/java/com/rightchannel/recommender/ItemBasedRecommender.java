package com.rightchannel.recommender;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.impl.model.file.FileDataModel;
import org.apache.mahout.cf.taste.impl.recommender.BiasedItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.recommender.IDRescorer;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;
import org.apache.mahout.common.iterator.FileLineIterable;

import com.mongodb.MongoException;
import com.rightchannel.rescorer.OverallRescorer;

public class ItemBasedRecommender {

	public static HashMap<Long, Long> mid2year = new HashMap<Long, Long>();
	public static HashMap<Long, String> mid2title = new HashMap<Long, String>();
	public static HashMap<Long, Double> mid2rating = new HashMap<Long, Double>();

	public static void main(String[] args) throws TasteException,
			MongoException, IOException {
		String ml10mFolder = "/home/yapianyu/Desktop/movielens/ml-10M100K/refinement/";
		String ratingFilePath = ml10mFolder + "ratings.dat";
		String movieFilePath = ml10mFolder + "movies.dat";

		for (String line : new FileLineIterable(new File(movieFilePath), false)) {
			String[] fields = line.split("::");
			long id = Long.parseLong(fields[0]);
			long year = Long.parseLong(fields[1].substring(
					fields[1].length() - 5, fields[1].length() - 1));
			String title = fields[3];
			try {
				double rating = Double.parseDouble(fields[4]);
				mid2rating.put(id, rating);
			} catch (Exception e) {
				mid2rating.put(id, Double.NaN);
			}
			mid2year.put(id, year);
			mid2title.put(id, title);
		}

		DataModel model = new FileDataModel(new File(ratingFilePath));
		ItemSimilarity similarity = new PearsonCorrelationSimilarity(model);
		Recommender recommender = new BiasedItemBasedRecommender(model,
				similarity);
		IDRescorer rescorer = new OverallRescorer();
		List<RecommendedItem> recommendations = recommender.recommend(72000,
				1000, rescorer);
		for (RecommendedItem recommendation : recommendations) {
			long mid = recommendation.getItemID();
			System.out.println(String.format("%.3f\t%d\t%.1f\t%s(%d)",
					recommendation.getValue(), mid2year.get(mid),
					mid2rating.get(mid), mid2title.get(mid), mid));
		}
	}
}