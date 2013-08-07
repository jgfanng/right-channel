package com.moviecomes.demo.rescorer;

import org.apache.mahout.cf.taste.recommender.IDRescorer;

import com.moviecomes.demo.evaluation.BiasedItemBasedRecommendation;

public class YearRescorer implements IDRescorer {

	@Override
	public double rescore(long id, double originalScore) {
		// TODO Auto-generated method stub
		return originalScore;
	}

	@Override
	public boolean isFiltered(long id) {
		return BiasedItemBasedRecommendation.mid2year.get(id) < 1990;
	}

}
