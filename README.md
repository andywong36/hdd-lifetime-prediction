# hdd-lifetime-prediction
A quick ML inference engine to predict the remaining life of your hard drive

This is an implementation of the model described by the Amram et al. (2021). It use Backblaze data in order to train an AI that can predict the expected life left out of a hard drive. 

# Usage

A basic example of this tool can be shown below:

`sudo smartctl -a /dev/sdX | curl -d @- http://andywong.io/hdd-lifetime-prediction/`

## Output:
```
> This drive has a remaining life of 250 days (low: 125, high: 500)
```
