Specifications
==============

plurueiel ou masculin après forme défaut !!!

```
block:: ---> \SetKwBlock
    Actions = Actions
    Begin   = Début

```
input:: ---> \SetKwInput


word:: ---> \SetKw

for:: ---> \SetKwFor

ForEach = Pour Chaque

repeat:: ---> \SetKwRepeat{Repeat}{Répéter}{{Jusqu'à Avoir}}


repeat::
    Repeat = Répéter
           | Jusqu'à Avoir // Fin et début

ordre important !!!
           switch:: ---> \SetKwSwitch{Switch}{Case}{Other}%
               Switch = Suivant
               Case   = Cas
               Other  = Autre

           ifelif:: ---> \SetKwIF{If}{ElseIf}{Else}%


In   = Entrée
Ins  = // Vide indique de prendre version snas s et d'ajoutéer un s si cela existe, sinon on à le mêm texte que la clé !!!
