# Stochastic Optimization

Compares the following three stochastic optimization methods to a myopic and leave-alone strategy for finding the optimal strategy to allocate additional but limited resources to detection threat analysis:

* Adaptive Dynamic Programming (ADP_Table_Generator1.py)
* Evolutionary Strategies (ES_rolling.py)
* Non-Anticipativy Multi-stage Stochastic Programming (NonAnt.py)


The three methodologies to be compared are be applied to a single IDS problem with the following constraints:

* Horizon -- A single horizon period is 14 days or 336 hours
* Threat Arrivals -- Potential threats which must be assessed by an analyst arrive at a Poisson average rate of 50 per hour per sensor at the beginning of the hour. Typical of IDSs, the severity and validity of the threat is unknown prior to processing
* Service Rates -- In reality, the time taken to analyze an alert depends on its severity, whether or not it is part of a known pattern, and the expertise level of the analyst\cite{ganesan_approximate_2017}. However, to constrain the problem size, the assumption will be made that a single analyst is capable of reviewing the threat at a deterministic rate of 51 threats per hour
* Resource Availabilities -- The system possesses 10 sensors and a constant 10 analysts hours are available per hour (i.e. 10 analysts are on staff at all times). 7 additional analyst hours are available and can be applied at the beginning of any hour during the problem horizon
* Risk Utility Metric -- the risk utility metric will consist of a simple subdivision:	green zone if queue >= 50; yellow zone if 50 < queue <= 100; red zone if queue > 100

The additional 7 hours of analytical resources will be distributed to manage the company's threat detection queue according to the risk utility metric above and minimize the extra resources expended to do so.


The Master_File.py contains the application of these files to the problem
