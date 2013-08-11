package com.moviecomes.rescorer;

import java.net.UnknownHostException;

import org.apache.mahout.cf.taste.recommender.IDRescorer;
import org.bson.types.ObjectId;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.MongoClient;
import com.mongodb.MongoException;
import com.moviecomes.recommender.MovieRecommender;

public class RatingRescorer implements IDRescorer {

	private MongoClient mongoClient;
	private DB db;
	private DBCollection movieColl;

	public RatingRescorer() throws UnknownHostException, MongoException {
		mongoClient = new MongoClient("127.0.0.1", 27017);
		db = mongoClient.getDB("right-channel");
		movieColl = db.getCollection("movies");
	}

	@Override
	public double rescore(long id, double originalScore) {
		// TODO Auto-generated method stub
		return originalScore;
	}

	@Override
	public boolean isFiltered(long id) {
		String movieIdStr = MovieRecommender.model.fromLongToId(id);
		if (movieIdStr == null)
			return true;

		ObjectId movieIdObj = new ObjectId(movieIdStr);
		DBObject movieObj = movieColl.findOne(new BasicDBObject("_id",
				movieIdObj));
		if (movieObj == null
				|| movieObj.get("douban") == null
				|| ((Number) ((BasicDBObject) movieObj.get("douban"))
						.get("rating")).doubleValue() < 6)
			return true;

		return false;
	}

}
