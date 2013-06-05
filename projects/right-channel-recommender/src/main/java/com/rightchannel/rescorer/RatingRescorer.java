package com.rightchannel.rescorer;

import org.apache.mahout.cf.taste.recommender.IDRescorer;

import com.rightchannel.recommender.ItemBasedRecommender;

public class RatingRescorer implements IDRescorer {

	@Override
	public double rescore(long id, double originalScore) {
		// TODO Auto-generated method stub
		return originalScore;
	}

	@Override
	public boolean isFiltered(long id) {
		double rating = ItemBasedRecommender.mid2rating.get(id);
		return Double.isNaN(rating) || rating < 6;
	}

}
