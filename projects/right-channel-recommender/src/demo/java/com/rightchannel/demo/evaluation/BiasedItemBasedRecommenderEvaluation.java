package com.rightchannel.demo.evaluation;

import java.io.File;
import java.io.IOException;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.common.Weighting;
import org.apache.mahout.cf.taste.eval.RecommenderBuilder;
import org.apache.mahout.cf.taste.eval.RecommenderEvaluator;
import org.apache.mahout.cf.taste.example.grouplens.GroupLensDataModel;
import org.apache.mahout.cf.taste.impl.eval.AverageAbsoluteDifferenceRecommenderEvaluator;
import org.apache.mahout.cf.taste.impl.recommender.BiasedItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;

public class BiasedItemBasedRecommenderEvaluation {

	public final static String ratingsFilePath = "/home/yapianyu/Desktop/movielens/ml-10M100K/ratings.dat";

	public static void main(String[] args) throws IOException, TasteException {
		itemBasedUnweighted();// MAE: 0.667200291477032
		itemBasedWeighted();// MAE: 0.668427549180065
	}

	public static void itemBasedUnweighted() throws IOException, TasteException {
		DataModel model = new GroupLensDataModel(new File(ratingsFilePath));
		RecommenderEvaluator evaluator = new AverageAbsoluteDifferenceRecommenderEvaluator();
		RecommenderBuilder recommenderBuilder = new RecommenderBuilder() {
			@Override
			public Recommender buildRecommender(DataModel model)
					throws TasteException {
				ItemSimilarity similarity = new PearsonCorrelationSimilarity(
						model);
				return new BiasedItemBasedRecommender(model, similarity);
			}
		};
		double score = evaluator.evaluate(recommenderBuilder, null, model,
				0.95, 0.05);
		System.out.println("MAE: " + score);
	}

	public static void itemBasedWeighted() throws IOException, TasteException {
		DataModel model = new GroupLensDataModel(new File(ratingsFilePath));
		RecommenderEvaluator evaluator = new AverageAbsoluteDifferenceRecommenderEvaluator();
		RecommenderBuilder recommenderBuilder = new RecommenderBuilder() {
			@Override
			public Recommender buildRecommender(DataModel model)
					throws TasteException {
				ItemSimilarity similarity = new PearsonCorrelationSimilarity(
						model, Weighting.WEIGHTED);
				return new BiasedItemBasedRecommender(model, similarity);
			}
		};
		double score = evaluator.evaluate(recommenderBuilder, null, model,
				0.95, 0.05);
		System.out.println("MAE: " + score);
	}
}
