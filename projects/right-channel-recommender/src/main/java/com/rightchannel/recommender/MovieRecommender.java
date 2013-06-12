package com.rightchannel.recommender;

import java.net.UnknownHostException;
import java.util.List;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.impl.model.mongodb.MongoDBDataModel;
import org.apache.mahout.cf.taste.impl.recommender.BiasedItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.recommender.IDRescorer;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;
import org.bson.types.ObjectId;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.Mongo;
import com.mongodb.MongoException;
import com.rightchannel.rescorer.OverallRescorer;

public class MovieRecommender {

	public static MongoDBDataModel model;

	public static void main(String[] args) throws TasteException,
			UnknownHostException, MongoException {
		model = new MongoDBDataModel("127.0.0.1", 27017, "right-channel",
				"ratings", false, false, null, "user_id", "movie_id", "rating",
				MongoDBDataModel.DEFAULT_MONGO_MAP_COLLECTION);

		ItemSimilarity similarity = new PearsonCorrelationSimilarity(model);
		Recommender recommender = new BiasedItemBasedRecommender(model,
				similarity);
		IDRescorer rescorer = new OverallRescorer();
		List<RecommendedItem> recommendations = recommender.recommend(Long
				.parseLong(model.fromIdToLong(new ObjectId(
						"518ce9df4597b5adead4b61d").toStringMongod(), false)),
				1000, rescorer);

		Mongo mongoDB = new Mongo("127.0.0.1", 27017);
		DB db = mongoDB.getDB("right-channel");
		DBCollection recommendationCollection = db
				.getCollection("recommendations");

		BasicDBObject document = new BasicDBObject();
		document.put("user_id", new ObjectId("518ce9df4597b5adead4b61d"));
		recommendationCollection.remove(document);

		for (RecommendedItem recommendation : recommendations) {
			long movieIdLong = recommendation.getItemID();
			String movieIdString = model.fromLongToId(movieIdLong);
			ObjectId movieIdObject = new ObjectId(movieIdString);
			double rating = recommendation.getValue();

			BasicDBObject prediction = new BasicDBObject();
			Object userIdObject = new ObjectId("518ce9df4597b5adead4b61d");
			prediction.put("user_id", userIdObject);
			prediction.put("movie_id", movieIdObject);
			prediction.put("rating", rating);
			recommendationCollection.insert(prediction);
			
			System.out.println(rating);
		}
	}
}