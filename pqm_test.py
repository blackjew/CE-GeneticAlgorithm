import Problem
import Crossover_op as C
import Mutation_op as M
import ParentSelection_op as P
import GenerationSelection_op as G
import Experiment as exp
import plot
from GA import GA
import util
import pqm
import Constraint_op as Cons
import math
import pickle
import os
import numpy as np

def pqm_class(param, train_class, test_class=None):
    train_X, train_y = util.load_dataset('SPECT.train', 1)
    pqm_class = [train_class]
    
    train_X0 = [sample[0] for sample in zip(train_X,train_y) if sample[1] == pqm_class]
    
    test_X, test_y = util.load_dataset('SPECT.test', 1)
    
    if test_class != None:
        test_class = [test_class]
        test_X = [sample[0] for sample in zip(test_X,test_y) if sample[1] == test_class]
        test_y = [test_class]*len(test_X)
    
    pqm_classifier = pqm.PQMClassifier(train_X0, pqm_class)
    
    error = 0
    for i in range(len(test_X)):
        result = pqm_classifier.classify(test_X[i], param)
        #print(result, test_y[i], pqm_classifier.pqm_class)
        
        if test_y[i] == pqm_classifier.pqm_class:
            error += (1 - result)**2
        else:
            error += result**2
            
        #print(pqm_class, error)
    
    print(error/len(test_X))
    
def wlnn_class(params, train_classes, test_class=None):
    train_X, train_y = util.load_dataset('SPECT.train', 1)
    
    divided_samples = {str(train_class): [] for train_class in train_classes}
    #print(divided_samples)
    
    for sample, label in zip(train_X, train_y):
        label = ''.join(map(str, label))
        divided_samples[label].append(sample)
        
    test_X, test_y = util.load_dataset('SPECT.test', 1)
    
    if test_class != None:
        test_class = [test_class]
        test_X = [sample[0] for sample in zip(test_X,test_y) if sample[1] == test_class]
        test_y = [test_class]*len(test_X)
    
    # setup pqms and wlnn
    c_bits = 1
    pqms = []
    for label in divided_samples.keys():
        #print(list(label))
        pqms.append(pqm.PQMClassifier(divided_samples[label], c_bits, [int(label)]))
    
    #print(pqms)
    wlnn = pqm.WLNN(pqms)
    
    hits = 0
    for i in range(len(test_X)):
        result = wlnn.classify(test_X[i], params)
        #print(result, test_y[i])
        
        if result == test_y[i]:
            hits += 1
    
    acc = hits/len(test_X)
    return acc

def pqm_exp():
    #experiments = []
    
    #GA
    pop_size = 100
    parents_n = pop_size/2
    limit = 10
    
    #pqm
    solution_size = 15
    precision = solution_size-1
    gene_range = (0,1)
    p_type = "MIN"
    
    #operator
    sample_size = 5
    mutation_rate = 0.1
    
    #executions
    #n = 50
    n=1
    
    #setup pqm classifier
    train_X, train_y = util.load_dataset('SPECT.train', 1)
    pqm_class = [0]
    
    train_X0 = [sample[0] for sample in zip(train_X,train_y) if sample[1] == pqm_class]
    
    test_X, test_y = util.load_dataset('SPECT.test', 1)
    
    pqm_classifier = pqm.PQMClassifier(train_X0, pqm_class)
    
    problem = Problem.PQMProblem('pqm', solution_size, precision, gene_range, p_type, pqm_classifier, test_X, test_y)
    
    point_crossover = C.OnePointCrossover()
    uniform_crossover = C.UniformCrossover(p=0.5)
    
    #random_point_mutation = M.RandomPointMutation(mutation_rate)
    resetting_mutation = M.RandomResettingMutation(mutation_rate)
    swap_mutation = M.SwapMutation(mutation_rate)
    
    tournament_parent = P.ParentTournamentSelection(sample_size)
    uniform_parent = P.ParentUniformSelection(0.2)
    
    elitist_selection = G.ElitistSelection()
    robin_selection = G.RoundRobinSelection(sample_size)
    
    #constraint
    cons = Cons.Constraint_allZero()
    
    #1
    algs = []
    #algs.append(GA("Variação alta", problem, uniform_crossover, resetting_mutation, uniform_parent, robin_selection, pop_size=pop_size, parents_n=parents_n, limit=limit, constraint=cons))
    algs.append(GA("Pressão evolutiva alta", problem, point_crossover, swap_mutation, tournament_parent, elitist_selection, pop_size=pop_size, parents_n=parents_n, limit=limit, constraint=cons))
    
    exps = []
    for alg in algs:
        e = exp.Experiment(alg.name)
        e.run(alg,n)
        exps.append(e)
    
    plot.plot(exps, 'Extremos')
    
def wlnn_exp():
    #experiments = []
    
    #GA
    pop_size = 200
    parents_n = pop_size/2
    limit = 30
    
    #pqm
    solution_size = 15
    precision = solution_size
    gene_range = (0,1)
    p_type = "MAX"
    
    #operator
    sample_size = 5
    mutation_rate = 0.1
    
    #executions
    #n = 50
    n=1
    
    
    train_X, train_y = util.load_dataset('SPECT.train', 1)
    #setup train dataset
    train_classes = [0,1]
    divided_samples = {str(train_class): [] for train_class in train_classes}
    #print(divided_samples)
    
    for sample, label in zip(train_X, train_y):
        label = ''.join(map(str, label))
        divided_samples[label].append(sample)
    
    # setup pqms and wlnn
    c_bits = 1
    pqms = []
    for label in divided_samples.keys():
        #print(list(label))
        pqms.append(pqm.PQMClassifier(divided_samples[label], c_bits, [int(label)]))
    
    #print(pqms)
    wlnn_classifier = pqm.WLNN(pqms)
    
    test_X, test_y = util.load_dataset('SPECT.test', 1)
    
    #problem = Problem.PQMProblem('pqm', solution_size, precision, gene_range, p_type, pqm_classifier, test_X, test_y)
    
    problem = Problem.WLNNProblem('wlnn', solution_size, precision, gene_range, p_type, wlnn_classifier, test_X, test_y)
    
    point_crossover = C.OnePointCrossover()
    uniform_crossover = C.UniformCrossover(p=0.5)
    
    #random_point_mutation = M.RandomPointMutation(mutation_rate)
    resetting_mutation = M.RandomResettingMutation(mutation_rate)
    swap_mutation = M.SwapMutation(mutation_rate)
    
    tournament_parent = P.ParentTournamentSelection(sample_size)
    uniform_parent = P.ParentUniformSelection(0.2)
    
    elitist_selection = G.ElitistSelection()
    robin_selection = G.RoundRobinSelection(sample_size)
    
    #constraint
    cons = Cons.Constraint_allZero()
    
    #1
    algs = []
    #algs.append(GA("Variação alta", problem, uniform_crossover, resetting_mutation, uniform_parent, robin_selection, pop_size=pop_size, parents_n=parents_n, limit=limit, constraint=cons))
    algs.append(GA("Pressão evolutiva alta", problem, point_crossover, swap_mutation, tournament_parent, elitist_selection, pop_size=pop_size, parents_n=parents_n, limit=limit, constraint=cons))
    
    exps = []
    for alg in algs:
        e = exp.Experiment(alg.name)
        e.run(alg,n)
        exps.append(e)
    
    name = 'solutions'
    sols = algs[0].solutions
    save_solutions(name, sols)
    obj = load_solutions(name)
    
    plot.plot(exps, 'Extremos')
    
def save_solutions(name, solutions):
    with open(name+".p", "wb" ) as file:
        pickle.dump(solutions, file)

def load_solutions(name):
    with open(name+".p", "rb" ) as file:
        solutions = pickle.load(file)
    
    return solutions

if __name__ == '__main__':
    #pqm_exp()
    wlnn_exp()
    #os.system('shutdown -s')
#    param = 0.90120
#    param2 = 0.90029
#    param3 = 0.90029515745119333168095970479165924594311356191920307568205
#    param4 = 0.90029260494972064130373071597454901043957143939591620501362517967593379524004220927650608005857953241695501154
#    paramC = 0.14336
#    #param2 =
#    #p1 = 0.21120
#    #p2 = 0.23711
#    p3 = 0.29225
#    p4 = 0.22944
#    #pqm_class(p3, 0, test_class=0)
#    #pqm_class(p4, 1, test_class=0)
#    
#    vs = [0.87253771, 0.84823509]
#    #vs = [0.872, 0.848]
#    vs2 = [2.44555785, 2.40351672]
#    vs3 = [95.10520537, 93.83000869]
#    vs4 = [5.22369309, 5.15449209]
#    vs5 = [p3, p4]
#    vs6 = [0.11551, 0.6620]
#    r = wlnn_class(vs, [0,1], test_class=None)
#    r2 = wlnn_class(vs2, [0,1], test_class=None)
#    r3 = wlnn_class(vs3, [0,1], test_class=None)
#    r4 = wlnn_class(vs4, [0,1], test_class=None)
#    r5 = wlnn_class(vs5, [0,1], test_class=None)
#    r6 = wlnn_class(vs6, [0,1], test_class=None)
#    print(r)
#    print(r2)
#    print(r3)
#    print(r4)
#    print(r5)
#    print(r6)
#    values = np.linspace(0.87253771, 1, num=20, endpoint=True)
#    #print(values)
#    best = {'v': None, 'perf': 0}
#    for i in range(len(values)):
#        for j in range(i, len(values)):
#            v1 = values[i]
#            v2 = values[j]
#            print('v',v1,v2)
#            r = wlnn_class([v1,v2], [0,1], test_class=None)
#            print(r)
#            
#            if r > best['perf']:
#                best['perf'] = r
#                best['v'] = str(1) + ' | ' + str(v2)
#    
#    print(best)
        
#    0.23855880806830695
#    0.23855880806830695
#    
#    0.23855843631203175
#    0.23855843631203175