# hdd-lifetime-prediction
A quick ML inference engine to predict the remaining life of your hard drive

This is an implementation of the model described by the Amram et al. (2021). It use Backblaze data in order to train an AI that can predict the expected life left out of a hard drive. 

# Usage

A basic example of this tool can be shown below:

``` sh
docker build -t hdd-lifetime-prediction-app .
docker run -p 8080:8080 hdd-lifetime-prediction-app

sudo smartctl -A /dev/sdX | curl -X POST -H "Content-Type: text/plain" --data-binary @- localhost:8080/hdd-lifetime-prediction/
```

## Output:
```
{
  "predicted_lifetime": 276.3315409152338,
  "predicted_stats": {
    "expected_lifetime": 276.3315409152338,
    "lower_lifetime": 21.086563249558207,
    "lower_node": null,
    "median_lifetime": 263.7432142532636,
    "n_samples": 6167,
    "split_feature": null,
    "split_threshold": 0.0,
    "upper_lifetime": 608.2135071357179,
    "upper_node": null
  }
}
```
