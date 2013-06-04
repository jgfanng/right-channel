package com.rightchannel.recommender;

import java.net.UnknownHostException;
import java.util.List;
import java.util.Map;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.impl.model.mongodb.MongoDBDataModel;
import org.apache.mahout.cf.taste.impl.neighborhood.NearestNUserNeighborhood;
import org.apache.mahout.cf.taste.impl.recommender.GenericUserBasedRecommender;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.neighborhood.UserNeighborhood;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.UserSimilarity;
import org.bson.types.ObjectId;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.Mongo;
import com.mongodb.MongoException;

public class UserBasedRecommender {

	public static void main(String[] args) throws TasteException,
			UnknownHostException, MongoException {
		String ratingCollection = "ratings";

		Mongo mongoDDBB = new Mongo("127.0.0.1", 27017);
		DB db = mongoDDBB.getDB("right-channel");
		DBCollection collection = db.getCollection("movies");

		// DBObject objectIdLong = collection.findOne(new BasicDBObject("_id",
		// new ObjectId("515fed2456b0e7b458948ecc")));
		// Map<String, Object> idLong = (Map<String, Object>)
		// objectIdLong.toMap();
		// Object i = ((BasicDBObject)idLong.get("douban")).get("rating");

		MongoDBDataModel model = new MongoDBDataModel("127.0.0.1", 27017,
				"right-channel", ratingCollection, false, false, null,
				"user_id", "movie_id", "rating",
				MongoDBDataModel.DEFAULT_MONGO_MAP_COLLECTION);
		UserSimilarity similarity = new PearsonCorrelationSimilarity(model);
		UserNeighborhood neighborhood = new NearestNUserNeighborhood(100,
				similarity, model);
		Recommender recommender = new GenericUserBasedRecommender(model,
				neighborhood, similarity);
		List<RecommendedItem> recommendations = recommender.recommend(Long
				.parseLong(model.fromIdToLong(new ObjectId(
						"518ce9df4597b5adead4b61d").toStringMongod(), false)),
				1000);
		for (RecommendedItem recommendation : recommendations) {
			ObjectId movie_id = new ObjectId(model.fromLongToId(recommendation
					.getItemID()));
			DBObject objectIdLong = collection.findOne(new BasicDBObject("_id",
					movie_id));
			Map<String, Object> idLong = (Map<String, Object>) objectIdLong
					.toMap();

			System.out.println(recommendation.getValue() + "\t"
					+ idLong.get("year") + "\t"
					+ ((BasicDBObject) idLong.get("douban")).get("rating")
					+ "\t" + idLong.get("title") + "\t"
					+ idLong.get("original_title") + "\t"
					+ model.fromLongToId(recommendation.getItemID()));

		}
//		for (RecommendedItem recommendation : recommendations)
//			System.out.println(recommendation);
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