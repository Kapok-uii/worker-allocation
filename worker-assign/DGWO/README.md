#DGWO 

This project addresses the complex worker allocation challenge in ship block assembly job shops operating through two sequential stages: 

Component Processing Stage: Machining operations on diverse components 

Final Assembly Stage: Assembly of processed components under strict buffer-free conditions 

Key operational constraints: 

Task transfers dynamically adapt to actual progress (not fixed cycles) 

Transfer initiation requires downstream equipment availability 

Multi-skilled workforce with heterogeneous proficiency levels 

Task-specific limitations on assignable worker counts 

Core Challenge: Develop optimal worker-task allocation strategy minimizing total completion time while maintaining predetermined operation sequences.


Core Modules

Discrete Position Encoding 
﻿ 
Worker assignments represented as discrete permutation vectors 
﻿ 
Position mapping to feasible task-worker combinations 
﻿ 
Dual Initialization Strategies 
﻿ 
Rule-based initialization considering worker proficiency 
﻿ 
Random initialization for diversity preservation 
﻿ 
Hierarchical Conflict Resolution 
﻿ 
confictsolve.py: Passive conflict resolution 
﻿ 
checkor.py: Active conflict resolution 
﻿ 
Critical path seek via seek_critical_node.py 
﻿ 
Improved Discrete Grey Wolf Optimization evloution via gwonewpop.py


