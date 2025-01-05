from Main_Operands.MathOperation import MathOperationDataModel

from Data.Type_Convertors import DecimalData,IntegerData

from qtpynodeeditor import NodeData, NodeDataModel, NodeDataType,NodeValidationState, Port, PortType


class AdditionModel(MathOperationDataModel):
    name = "Addition"

    def compute(self):
        self._result = DecimalData(self._number1.number + self._number2.number)



class DivisionModel(MathOperationDataModel):
    name = "Division"
    port_caption = {'input': {0: 'Dividend',
                              1: 'Divisor',
                              },
                    'output': {0: 'Result'},
                    }

    def compute(self):
        if self._number2.number == 0.0:
            self._validation_state = NodeValidationState.error
            self._validation_message = "Division by zero error"
            self._result = None
        else:
            self._validation_state = NodeValidationState.valid
            self._validation_message = ''
            self._result = DecimalData(self._number1.number / self._number2.number)


class ModuloModel(MathOperationDataModel):
    name = 'Modulo'
    data_type = IntegerData.data_type
    port_caption = {'input': {0: 'Dividend',
                              1: 'Divisor',
                              },
                    'output': {0: 'Result'},
                    }

    def compute(self):
        if self._number2.number == 0.0:
            self._validation_state = NodeValidationState.error
            self._validation_message = "Division by zero error"
            self._result = None
        else:
            self._result = IntegerData(self._number1.number % self._number2.number)

class MultiplicationModel(MathOperationDataModel):
    name = 'Multiplication'
    port_caption = {'input': {0: 'A',
                              1: 'B',
                              },
                    'output': {0: 'Result'},
                    }

    def compute(self):
        self._result = DecimalData(self._number1.number * self._number2.number)




class SubtractionModel(MathOperationDataModel):
    name = "Subtraction"
    port_caption = {'input': {0: 'Minuend',
                              1: 'Subtrahend'},
                    'output': {0: 'Result'}, }

    def compute(self):
        self._result = DecimalData(self._number1.number - self._number2.number)
