import  datetime

class storeMoves():
    
    def __init__(self):
        self.history = []

    def add(self, move):
        self.history.append(move)

    def save(self):
        now = datetime.datetime.now()
        # save to a new file
        with open('games/%s.txt' % now.strftime("%c"), 'w') as filehandle:  
            for listitem in self.history:
                filehandle.write('%s\n' % listitem)
        # overwrite last.txt
        with open('games/last.txt', 'w') as filehandle:  
            for listitem in self.history:
                filehandle.write('%s\n' % listitem)
    

# usage example:
# storeMoves = storeMoves()
# storeMoves.add("a1b1")
# storeMoves.add("a3b2")
# storeMoves.save()