"""Musing on rules
Applied only if all end results are valid"""

name = "mustardFactory"
rate = 10

"""
unitRule mustardFactory
    rate 10 #Happens every 10 ticks
    
    global Simoleans in 1 #Takes one from global wallet bin 
    
    local YellowMustard in 6 #Takes from local bin
    local EmptyBottle in 1
    local BottleOfMustard out 1 #Puts in local bin
    
    map Pollution out 5 #Puts 5 units of pollution resource on pollution map
    
    successEvent effect smokePuff
    successEvent audio chugAndSlurp
    
    onFail buyMoreMustard #runs this rule on fail?
end
"""

"""Map rules
can opterate on entire map or colelction of random cells
run resource rule per cell but can reference multiple maps at once
or perform more specialised operation such as deffusion (second map) or advection (wind direction))

mapRule growGrass
    rate 200
    
    map Soil atLeast 20
    
    map Water in 10
    map Nutrients in 1
    
    map Grass out 5
end"""