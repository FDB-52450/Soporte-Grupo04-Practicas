from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ListProperty, StringProperty, BooleanProperty

class CalculatorApp(App):
    tempNum = ''
    valueList = ListProperty([])
    result = StringProperty('')
    blocked = BooleanProperty(False)
    
    def handleNumberPress(self, num: int):
        if not(self.blocked):
            self.tempNum += str(num)
    
    def handleOperatorPress(self, operator: str):
        if not(self.tempNum == ''):
            self.valueList.append(int(self.tempNum))
        elif self.result != '':
            self.valueList.append(int(self.result))
        else:
            self.handleError()
            
            return   
        
        self.valueList.append(operator)  
        self.tempNum = ''  
    
    def handleResultPress(self):
        if not(self.blocked):
            if not(self.tempNum == ''):
                self.valueList.append(int(self.tempNum))
                
            res = str(self.evaluate(self.valueList))
            
            if res is not None:
                self.result = str(res)
                self.tempNum = str(res)
                self.valueList = []
    
    def handleDeletePress(self):
        if not(self.blocked):
            self.tempNum = ''
            self.valueList = []
            self.result = ''
    
    def handleError(self):
        self.blocked = True
        self.result = 'ERROR'
        
        Clock.schedule_once(self.resetCalculator, 3)
    
    def resetCalculator(self, dt):
        self.tempNum = ''
        self.valueList = []
        self.result = ''
        self.blocked = False
    
    def evaluate(self, tokens):
        i = 0
        
        while i < len(tokens):
            if tokens[i] == '*':
                tokens[i-1:i+2] = [tokens[i-1] * tokens[i+1]]
                i -= 1
            elif tokens[i] == '/':
                if not(tokens[i+1] == 0):
                    tokens[i-1:i+2] = [tokens[i-1] / tokens[i+1]]
                    i -= 1
                else:
                    self.handleError()
                    
                    return
            else:
                i += 1

        result = tokens[0]
        i = 1
        
        while i < len(tokens):
            if tokens[i] == '+':
                result += tokens[i+1]
            elif tokens[i] == '-':
                result -= tokens[i+1]
            i += 2

        return result

if __name__ == '__main__':
    CalculatorApp().run()