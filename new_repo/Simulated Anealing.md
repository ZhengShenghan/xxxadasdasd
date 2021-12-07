# Simulated Anealing

#### Parameters

| T     | initial temperature                       |
| ----- | ----------------------------------------- |
| L     | Length of Markov chain                    |
| k     | the speed rate of temperature drop        |
| T_END | end_temperature for the algorithm to stop |
| x_0   | initial solution                          |

#### What we need to set

Set L and T, the higher the T and L, the better probability of result, but more time

Set k, the smaller k, the faster the temperature drops. I plan to set k actively to make the algorithm converge faster



We define the energy to be the 1/(sum of profit) here

![A flowchart of the simulated-annealing algorithm. | Download Scientific  Diagram](https://www.researchgate.net/publication/329917885/figure/fig1/AS:708072221704199@1545828981418/A-flowchart-of-the-simulated-annealing-algorithm.jpg)

![image-20211206133338479](C:\Users\Eric Zheng\AppData\Roaming\Typora\typora-user-images\image-20211206133338479.png)