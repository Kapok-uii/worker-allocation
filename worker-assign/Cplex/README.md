# Cplex for the MILP of worker allocation

This project addresses the complex worker allocation challenge in ship block assembly job shops operating through two sequential stages: 

Component Processing Stage: Machining operations on diverse components 

Final Assembly Stage: Assembly of processed components under assembly line 

Key operational constraints: 

Task transfers dynamically adapt to actual progress (not fixed cycles) 

Transfer initiation requires downstream equipment availability 

Multi-skilled workforce with heterogeneous proficiency levels 

Task-specific limitations on assignable worker counts 

Core Challenge: Develop optimal worker-task allocation strategy minimizing total completion time while maintaining predetermined operation sequences.


Key Features 
﻿ 
MILP Modeling: Mathematical formulation of worker allocation problem 
﻿ 
CPLEX Optimization: High-performance solution with IBM ILOG CPLEX 
﻿ 
Dynamic Reassignment: Worker allocation adjusts at decision points 
﻿ 
Scalable Solution: Handles instances A1-A4 of varying complexity 
﻿ 
Comprehensive Output: Makespan + detailed task schedules

 License

This project is licensed under the MIT License - see the LICENSE file for details.