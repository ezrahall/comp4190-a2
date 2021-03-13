import numpy as np


class Factor(object):

    def __init__(self, variables, probabilities):
        if len(variables) != 0:

            self.variables = variables

            self.ids = dict()
            for i in range(len(variables)):
                self.ids[variables[i]] = [True, False]

            self.probabilitiesTable = np.array(probabilities)
            table = ()
            for i in range(len(variables)):
                table = table + (2,)
            self.probabilitiesTable = self.probabilitiesTable.reshape(table)

    def printRecursive(self, currentValue):
        if len(self.variables) == len(currentValue):
            for i in range(len(self.variables)):
                values = self.ids[self.variables[i]]
                print values[currentValue[i]],
                print(','),
            print(': '),
            print self.probabilitiesTable.item(currentValue)
        else:
            values = self.ids[self.variables[len(currentValue)]]
            for i in range(len(values)):
                nextTuple = (i,)
                self.printRecursive(currentValue + nextTuple)

    def printTable(self):

        currentValue = ()
        print(self.variables)
        self.printRecursive(currentValue)

    def copyFactor(self):
        factor = Factor([], [])
        factor.variables = list(self.variables)
        factor.ids = dict(self.ids)
        factor.probabilitiesTable = self.probabilitiesTable.copy()
        return factor

    def sortFactor(self):
        for i in xrange(0, len(self.variables) - 1):
            for j in xrange(0, len(self.variables) - 1 - i):
                if self.variables[i] > self.variables[i + 1]:
                    tmp = self.variables[i]
                    self.variables[i] = self.variables[i + 1]
                    self.variables[i + 1] = tmp
                    self.probabilitiesTable = np.swapaxes(self.probabilitiesTable, i, i + 1)

    @staticmethod
    def observe(factor, variable, value):

        factor = factor.copyFactor()

        indexVariable = factor.variables.index(variable)

        tuple = ()
        # for i in range(indexVariable):
        #     values = factor.ids[factor.variables[i]]
        #     tuple += slice(None),

        values = factor.ids[factor.variables[indexVariable]]
        indexValue = values.index(value)
        tuple += slice(indexValue, indexValue + 1),

        var = factor.variables[indexVariable]
        del factor.variables[indexVariable]

        del factor.ids[var]

        factor.probabilitiesTable = factor.probabilitiesTable[tuple]
        table = ()
        for i in range(len(factor.variables)):
            vals = factor.ids[factor.variables[i]]
            currentValue = (len(vals),)
            table = table + currentValue
        factor.probabilitiesTable = factor.probabilitiesTable.reshape(table)
        return factor

    @staticmethod
    def multiply(factorOne, factorTwo):

        factorOne.sortFactor()
        factorTwo.sortFactor()

        commonVariables = list()
        for var in factorOne.variables:
            if var in factorTwo.variables:
                commonVariables.append(var)
        for var in factorTwo.variables:
            if var in factorOne.variables:
                if not (var in commonVariables):
                    commonVariables.append(var)

        unionVariables = list(factorOne.variables)
        for var in factorTwo.variables:
            if not (var in commonVariables):
                unionVariables.append(var)

        commonVariables.sort()
        unionVariables.sort()

        factorOneTuple = ()
        factorTwoTuple = ()
        for var in unionVariables:
            if var in factorOne.variables:
                factorOneTuple += (len(factorOne.ids[var]),)
            else:
                factorOneTuple += (1,)
            if var in factorTwo.variables:
                factorTwoTuple += (len(factorTwo.ids[var]),)
            else:
                factorTwoTuple += (1,)

        probabilityTableOne = factorOne.probabilitiesTable.reshape(factorOneTuple)
        probabilityTableTwo = factorTwo.probabilitiesTable.reshape(factorTwoTuple)

        factor = Factor([], [])
        factor.probabilitiesTable = probabilityTableOne * probabilityTableTwo
        factor.variables = unionVariables
        factor.ids = dict()
        for var in unionVariables:
            if var in factorOne.ids:
                factor.ids[var] = list(factorOne.ids[var])
            if var in factorTwo.ids:
                factor.ids[var] = list(factorTwo.ids[var])
        return factor

    @staticmethod
    def sumout(factor, variable):

        factor = factor.copyFactor()

        varId = factor.variables.index(variable)
        del factor.variables[varId]

        del factor.ids[variable]

        factor.probabilitiesTable = factor.probabilitiesTable.sum(axis=varId)
        return factor

    @staticmethod
    def normalize(factor):

        factor = factor.copyFactor()

        sum = factor.probabilitiesTable.sum()
        factor.probabilitiesTable = factor.probabilitiesTable / sum
        return factor

    @staticmethod
    def inference(factorList, queryVariables, orderedHiddenVariablesList, evidenceList):

        for e in evidenceList:
            newFactorList = list()
            for factor in factorList:
                if e in factor.variables:
                    factorObserve = Factor.observe(factor, e, evidenceList[e])

                    newFactorList.append(factorObserve)
                else:
                    newFactorList.append(factor)
            factorList = newFactorList

        for i in orderedHiddenVariablesList:
            factorListMultiplied = list()
            factorListNormalized = list()

            for factor in factorList:
                if i in factor.variables:
                    factorListMultiplied.append(factor)
                else:
                    factorListNormalized.append(factor)

            factorProduct = reduce(Factor.multiply, factorListMultiplied)

            factorSumout = Factor.sumout(factorProduct, i)

            factorList = factorListNormalized
            factorList.append(factorSumout)

        factorProduct = reduce(Factor.multiply, factorList)

        result = Factor.normalize(factorProduct)
        return result


def main():
    f1 = Factor(['A'], [0.1, 0.9])

    f2 = Factor(['A', 'B'], [0.8, 0.2, 0.1, 0.9])

    f3 = Factor(['B', 'C'], [0.3, 0.7, 0.1, 0.9])

    fL = [f1, f2, f3]
    hL = ['A', 'B']
    ql = ['C']
    eL = dict()
    fRes = Factor.inference(fL, ql, hL, eL)
    fRes.printTable()


main()
