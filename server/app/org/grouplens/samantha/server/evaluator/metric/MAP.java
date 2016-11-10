package org.grouplens.samantha.server.evaluator.metric;

import com.fasterxml.jackson.databind.JsonNode;

import com.fasterxml.jackson.databind.node.ObjectNode;
import it.unimi.dsi.fastutil.doubles.DoubleArrayList;
import it.unimi.dsi.fastutil.doubles.DoubleList;
import org.grouplens.samantha.modeler.featurizer.FeatureExtractorUtilities;
import org.grouplens.samantha.server.predictor.Prediction;
import org.grouplens.samantha.server.config.ConfigKey;
import play.Logger;
import play.libs.Json;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class MAP implements Metric {
    private final MAPConfig config;
    private int cnt = 0;
    private DoubleList AP;

    public MAP(MAPConfig config) {
        this.config = config;
        this.AP = new DoubleArrayList(config.N.size());
        for (int i=0; i<config.N.size(); i++) {
            this.AP.add(0.0);
        }
    }

    public void add(List<ObjectNode> groundTruth, List<Prediction> recommendations) {
        Set<String> releItems = new HashSet<>();
        for (JsonNode entity : groundTruth) {
            if (config.ratingKey == null || entity.get(config.ratingKey).asDouble() >= config.leastRating) {
                String item = FeatureExtractorUtilities.composeConcatenatedKey(entity, config.itemKeys);
                releItems.add(item);
            }
        }
        if (releItems.size() == 0) {
            return;
        }
        int maxN = 0;
        for (Integer n : config.N) {
            if (n > maxN) {
                maxN = n;
            }
            if (recommendations.size() < n) {
                Logger.error("The number of recommendations({}) is less than the indicated MAP N({})",
                        recommendations.size(), n);
            }
        }
        int hits = 0;
        double[] ap = new double[config.N.size()];
        for (int i=0; i<recommendations.size(); i++) {
            int rank = i + 1;
            String recItem = FeatureExtractorUtilities.composeConcatenatedKey(
                    recommendations.get(i).getEntity(), config.itemKeys);
            int hit = 0;
            if (releItems.contains(recItem)) {
                hit = 1;
                hits += 1;
            }
            for (int j=0; j<config.N.size(); j++) {
                int n = config.N.get(j);
                if (rank <= n) {
                    ap[j] += (1.0 * hits / rank) * hit;
                }
            }
            if (rank > maxN) {
                break;
            }
        }
        for (int i=0; i<config.N.size(); i++) {
            AP.set(i, AP.getDouble(i) + ap[i] / releItems.size());
        }
        cnt += 1;
    }

    public List<ObjectNode> getValues() {
        List<ObjectNode> results = new ArrayList<>(config.N.size());
        ObjectNode metricPara = Json.newObject();
        for (int i=0; i<config.N.size(); i++) {
            ObjectNode result = Json.newObject();
            result.put(ConfigKey.EVALUATOR_METRIC_NAME.get(), "MAP");
            metricPara.put("N", config.N.get(i));
            result.put(ConfigKey.EVALUATOR_METRIC_PARA.get(),
                    metricPara.toString());
            if (cnt > 0) {
                result.put(ConfigKey.EVALUATOR_METRIC_VALUE.get(),
                        AP.getDouble(i) / cnt);
            } else {
                result.put(ConfigKey.EVALUATOR_METRIC_VALUE.get(), 0.0);
            }
            results.add(result);
        }
        return results;
    }
}
