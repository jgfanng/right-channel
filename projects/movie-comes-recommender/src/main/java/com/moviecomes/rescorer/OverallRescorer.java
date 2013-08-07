package com.moviecomes.rescorer;

import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.List;

import org.apache.mahout.cf.taste.recommender.IDRescorer;

import com.mongodb.MongoException;

public class OverallRescorer implements IDRescorer {

	private List<IDRescorer> rescorerPipeline;

	public OverallRescorer() throws UnknownHostException, MongoException {
		rescorerPipeline = new ArrayList<IDRescorer>();
		rescorerPipeline.add(new YearRescorer());
		rescorerPipeline.add(new RatingRescorer());
	}

	@Override
	public double rescore(long id, double originalScore) {
		double score = originalScore;
		for (IDRescorer rescorer : rescorerPipeline)
			score = rescorer.rescore(id, score);

		return score;
	}

	@Override
	public boolean isFiltered(long id) {
		for (IDRescorer rescorer : rescorerPipeline)
			if (rescorer.isFiltered(id))
				return true;

		return false;
	}

}
