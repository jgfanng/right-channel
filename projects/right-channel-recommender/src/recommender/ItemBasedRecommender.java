package recommender;

import java.io.File;
import java.io.IOException;
import java.net.UnknownHostException;
import java.util.List;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.impl.model.file.FileDataModel;
import org.apache.mahout.cf.taste.impl.model.mongodb.MongoDBDataModel;
import org.apache.mahout.cf.taste.impl.neighborhood.NearestNUserNeighborhood;
import org.apache.mahout.cf.taste.impl.recommender.GenericItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.recommender.GenericUserBasedRecommender;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.neighborhood.UserNeighborhood;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;
import org.apache.mahout.cf.taste.similarity.UserSimilarity;
import org.bson.types.ObjectId;

import com.mongodb.MongoException;

public class ItemBasedRecommender {

	public static void main(String[] args) throws TasteException,
			UnknownHostException, MongoException {
		MongoDBDataModel model = new MongoDBDataModel("127.0.0.1", 27017,
				"right-channel", "ml_100k_ratings", false, false, null,
				"user_id", "movie_id", "rating",
				MongoDBDataModel.DEFAULT_MONGO_MAP_COLLECTION);
		ItemSimilarity similarity = new PearsonCorrelationSimilarity(model);
		Recommender recommender = new GenericItemBasedRecommender(model,
				similarity);
		List<RecommendedItem> recommendations = recommender.recommend(Long
				.parseLong(model.fromIdToLong(new ObjectId(
						"51a0c3b3862f09377d71493c").toStringMongod(), false)),
				500);
		for (RecommendedItem recommendation : recommendations)
			System.out.println(recommendation);
		// try {
		// DataModel model = new FileDataModel(new File("intro.csv"));
		// UserSimilarity similarity = new PearsonCorrelationSimilarity(model);
		// UserNeighborhood neighborhood = new NearestNUserNeighborhood(5,
		// similarity, model);
		// Recommender recommender = new GenericUserBasedRecommender(model,
		// neighborhood, similarity);
		// List<RecommendedItem> recommendations = recommender.recommend(5, 1);
		// for (RecommendedItem recommendation : recommendations)
		// System.out.println(recommendation);
		// } catch (IOException e) {
		// // TODO Auto-generated catch block
		// e.printStackTrace();
		// }

	}

}