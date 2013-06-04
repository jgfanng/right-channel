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
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;
import org.apache.mahout.common.iterator.FileLineIterable;

import com.mongodb.MongoException;

public class ItemBasedRecommender {

	public static void main(String[] args) throws TasteException,
			MongoException, IOException {
		String ml10mFolder = "/home/yapianyu/Desktop/movielens/ml-10M100K/refinement/";
		String ratingFilePath = ml10mFolder + "ratings.dat";
		String movieFilePath = ml10mFolder + "movies.dat";

		DataModel model = new FileDataModel(new File(ratingFilePath));
		ItemSimilarity similarity = new PearsonCorrelationSimilarity(model);
		Recommender recommender = new BiasedItemBasedRecommender(model,
				similarity);
		List<RecommendedItem> recommendations = recommender.recommend(72000,
				1000);

		HashMap<Long, String> mid2minfo = new HashMap<Long, String>();
		for (String line : new FileLineIterable(new File(movieFilePath), false)) {
			String DELIMITER = "::";
			Long mid = Long
					.parseLong(line.substring(0, line.indexOf(DELIMITER)));
			mid2minfo.put(mid, line);
		}
		for (RecommendedItem recommendation : recommendations) {
			Long mid = recommendation.getItemID();
			System.out.println(String.format("%.3f", recommendation.getValue())
					+ "\t" + mid2minfo.get(mid));
		}
	}
}