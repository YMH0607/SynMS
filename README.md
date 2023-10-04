## Background
`SynMS` and `Enum` are the methods mentioned in paper to learn winning strategy of `Impartial Combinatorial Games`. 


## Install
```pip install -r requirements.txt```
System requirements: `Windows`

Running the nuwls-un solver requires Cygwin software that can provide a Linux simulation environment running on the Windows platform.You need download Cygwin packages from http://www.cygwin.com/install.html and add Cygwin to the system environment.
### Run the code with the following command:

`python <approach> <gameProblem> <resultFile> <gameType>`


```approach```: it is one of the Enum, SynMS

```gameProblem```: it is the path of game problem(.pddl file) 

```resultFile```: it is the path of resulet file(.txt file) 

```game_type```:it is the type of game(normal or misere)  

For example,  the game problem：Two-piled-nim.pddl
```
python SynMS.py "domain\2.Nim\2.1 Nim\Two-piled-nim.pddl" "test.xls" "normal"  
 ```


The result will be saved in the filr result.txt, which contains 5 columns : `game name | winning formula |	time of winning formula  | winning strategy |	time of winning strategy`.

## Benchmarks
We use PDDL to define the game problem, like this:
```
(define (domain Two-piled-nim)
	(:objects ?v1 ?v2)
	(:tercondition (and (= ?v1 0) (= ?v2 0) ))
    (:constraint (and (>= ?v1 0) (>= ?v2 0)))
    (:action take1
        :parameters (?k)
        :precondition (and (>= ?v1 ?k) (> ?k 0))
        :effect (assign ?v1 (- ?v1 ?k)))
    (:action take2
        :parameters (?k)
        :precondition (and (>= ?v2 ?k) (> ?k 0)) 
        :effect (assign ?v2 (- ?v2 ?k)))
)
```
All domain are stored in folder `domain`.

