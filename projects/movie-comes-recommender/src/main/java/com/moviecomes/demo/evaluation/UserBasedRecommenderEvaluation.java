package com.moviecomes.demo.evaluation;

import java.io.File;
import java.io.IOException;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.common.Weighting;
import org.apache.mahout.cf.taste.eval.RecommenderBuilder;
import org.apache.mahout.cf.taste.eval.RecommenderEvaluator;
import org.apache.mahout.cf.taste.example.grouplens.GroupLensDataModel;
import org.apache.mahout.cf.taste.impl.eval.AverageAbsoluteDifferenceRecommenderEvaluator;
import org.apache.mahout.cf.taste.impl.neighborhood.NearestNUserNeighborhood;
import org.apache.mahout.cf.taste.impl.recommender.GenericUserBasedRecommender;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.neighborhood.UserNeighborhood;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.UserSimilarity;

public class UserBasedRecommenderEvaluation {

	public final static String ratingsFilePath = "/home/yapianyu/Desktop/movielens/ml-10M100K/ratings.dat";

	public static void main(String[] args) throws IOException, TasteException {
		userBasedUnweighted();// MAE: 0.8359409772500003
		userBasedWeighted();// MAE: 0.8187451148143108
	}

	public static void userBasedUnweighted() throws IOException, TasteException {
		DataModel model = new GroupLensDataModel(new File(ratingsFilePath));
		RecommenderEvaluator evaluator = new AverageAbsoluteDifferenceRecommenderEvaluator();
		RecommenderBuilder recommenderBuilder = new RecommenderBuilder() {
			@Override
			public Recommender buildRecommender(DataModel model)
					throws TasteException {
				UserSimilarity similarity = new PearsonCorrelationSimilarity(
						model);
				UserNeighborhood neighborhood = new NearestNUserNeighborhood(
						100, similarity, model);
				return new GenericUserBasedRecommender(model, neighborhood,
						similarity);
			}
		};
		double score = evaluator.evaluate(recommenderBuilder, null, model,
				0.95, 0.05);
		System.out.println("MAE: " + score);
	}

	public static void userBasedWeighted() throws IOException, TasteException {
		DataModel model = new GroupLensDataModel(new File(ratingsFilePath));
		RecommenderEvaluator evaluator = new AverageAbsoluteDifferenceRecommenderEvaluator();
		RecommenderBuilder recommenderBuilder = new RecommenderBuilder() {
			@Override
			public Recommender buildRecommender(DataModel model)
					throws TasteException {
				UserSimilarity similarity = new PearsonCorrelationSimilarity(
						model, Weighting.WEIGHTED);
				UserNeighborhood neighborhood = new NearestNUserNeighborhood(
						100, similarity, model);
				return new GenericUserBasedRecommender(model, neighborhood,
						similarity);
			}
		};
		double score = evaluator.evaluate(recommenderBuilder, null, model,
				0.95, 0.05);
		System.out.println("MAE: " + score);
	}
}
