package com.rightchannel.rescorer;

import org.apache.mahout.cf.taste.recommender.IDRescorer;

import com.rightchannel.recommender.ItemBasedRecommender;

public class YearRescorer implements IDRescorer {

	@Override
	public double rescore(long id, double originalScore) {
		// TODO Auto-generated method stub
		return originalScore;
	}

	@Override
	public boolean isFiltered(long id) {
		return ItemBasedRecommender.mid2year.get(id) < 1990;
	}

}
