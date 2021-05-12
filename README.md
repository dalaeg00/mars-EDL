# Mars *Entry, Descent, & Landing* 1-D simulation
Development of a simplified model for a one-dimensional EDL mission in an artificially generated Mars atmosphere from scratch, using Python.

***
Thanks to *webplotdigitizer*, temperature data measured on the Viking 1 mission has been extracted into a .csv file: *viking1.csv*. After importing and normalizing the data with 
*Pandas*, a 7th degree polynomial fit has been implemented to obtain a continous temperature function for the first 120 km of altitude.

When executed, the graph shows a comparison between the polynomial fit, the original measured data, and a linear model proposed by NASA. Considering the similar model for the pressure equation, and using the gas properties from the *PDS Atmospheres Node*, density can be derived using the equation of state. With all three properties defined, the model itself is fully defined.

The simulation has been divided into three different stages (with their own governing equations):
1. **Stage 1**: Free fall from 30km high. Only drag forces from the heat shield are applied against gravity.
2. **Stage 2**: Parachute descent. Drag forces from both the parachute & the heat shield are considered. Aerodynamic interference between both is neglected to simplify the model, assuming long parachute chords.
3. **Stage 3**: Powered descent: Rocket equation is governing the last stage of descent, assuming a constant gas exhaust speed, without parachute.

Results show some disparity with the Perseverance mission official data. Most of the differences are due to some of the simplifications, as well as considering the descent control as an open loop without sensor data feedback, which fixes the conditions to their initial values.

For the aerodynamic coefficients, the Prandtl-Glauer correction has been implemented. Since there's a known singularity at Mach speeds close to 1, two ranges have been identified and assigned a fixed value, which act as a step function between Mach 0.7 and 1.3
***

By no means this simulation must be considered as an accurate representation of real world phenomena. It's been developed for education purposes, and it could only serve as a preliminary design tool based on previous data.
