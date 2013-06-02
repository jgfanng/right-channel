package recommender;

import java.io.File;
import java.io.IOException;
import java.util.List;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.impl.model.file.FileDataModel;
import org.apache.mahout.cf.taste.impl.recommender.GenericItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;

public class TestSimilarity {

	/**
	 * @param args
	 * @throws IOException
	 * @throws TasteException
	 */
	public static void main(String[] args) throws IOException, TasteException {
		DataModel model = new FileDataModel(new File("ratings.dat"));
		ItemSimilarity similarity = new PearsonCorrelationSimilarity(model);
		Recommender recommender = new GenericItemBasedRecommender(model,
				similarity);
		System.out.println(similarity.itemSimilarity(1, 3));
		System.out.println(similarity.itemSimilarity(2, 3));
		System.out.println(similarity.itemSimilarity(1, 2));
		List<RecommendedItem> recommendations = recommender.recommend(3, 1000);
		for (RecommendedItem recommendation : recommendations)
			System.out.println(recommendation);
	}

}
