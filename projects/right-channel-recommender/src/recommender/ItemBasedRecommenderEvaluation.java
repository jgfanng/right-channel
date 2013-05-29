package recommender;

import java.io.File;
import java.io.IOException;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.eval.RecommenderBuilder;
import org.apache.mahout.cf.taste.eval.RecommenderEvaluator;
import org.apache.mahout.cf.taste.example.grouplens.GroupLensDataModel;
import org.apache.mahout.cf.taste.impl.eval.AverageAbsoluteDifferenceRecommenderEvaluator;
import org.apache.mahout.cf.taste.impl.recommender.GenericItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;

public class ItemBasedRecommenderEvaluation {

	/**
	 * @param args
	 * @throws IOException
	 * @throws TasteException
	 */
	public static void main(String[] args) throws IOException, TasteException {
		DataModel model = new GroupLensDataModel(new File(
				"/home/yapianyu/Desktop/ml-1m/ratings.dat"));
		// RecommenderEvaluator evaluator = new RMSRecommenderEvaluator();
		RecommenderEvaluator evaluator = new AverageAbsoluteDifferenceRecommenderEvaluator();
		RecommenderBuilder recommenderBuilder = new RecommenderBuilder() {
			@Override
			public Recommender buildRecommender(DataModel model)
					throws TasteException {
				ItemSimilarity similarity = new PearsonCorrelationSimilarity(
						model);
				return new GenericItemBasedRecommender(model, similarity);
			}
		};
		double score = evaluator.evaluate(recommenderBuilder, null, model,
				0.95, 0.05);
		System.out.println(score);
	}

}
