package com.rightchannel.rescorer;

import java.net.UnknownHostException;

import org.apache.mahout.cf.taste.recommender.IDRescorer;
import org.bson.types.ObjectId;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.Mongo;
import com.mongodb.MongoException;
import com.rightchannel.recommender.MovieRecommender;

public class YearRescorer implements IDRescorer {

	private Mongo mongoDB;
	private DB db;
	private DBCollection movieCollection;

	public YearRescorer() throws UnknownHostException, MongoException {
		mongoDB = new Mongo("127.0.0.1", 27017);
		db = mongoDB.getDB("right-channel");
		movieCollection = db.getCollection("movies");
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
		DBObject movieObj = movieCollection.findOne(new BasicDBObject("_id",
				movieIdObj));
		if (movieObj == null || movieObj.get("year") == null)
			return true;

		try {
			if (Integer.parseInt((String) movieObj.get("year")) < 1990)
				return true;
		} catch (Exception e) {
			return true;
		}

		return false;
	}

}
