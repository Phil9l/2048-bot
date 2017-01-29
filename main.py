#!/usr/bin/env python

import sys
import operator
import random
import functools
import numpy

from argparse import ArgumentParser

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

from game.models import Direction, Field


DIRECTIONS = [Direction.LEFT, Direction.UP, Direction.RIGHT, Direction.DOWN]
toolbox = base.Toolbox()


def get_arguments():
    parser = ArgumentParser()
    parser.add_argument('-g', '--generations', type=int,
                        metavar='GENERATION_NUMBER', default=100,
                        help='Number of generations.')
    parser.add_argument('-s', '--seed', type=int,
                        metavar='SEED', help='Seed for random.')
    parser.add_argument('-p', '--preview', action='store_true',
                        help='Show how result algorithm works after finish.')

    parser.add_argument('--test', type=str, metavar='FUNCTION',
                        help='Seed for random.')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Run program in debug mode.')
    args = parser.parse_args()
    return args


def extract_data(tf):
    if isinstance(tf, tuple):
        field, status = tf
    else:
        field, status = tf, False
    return field, status


def move_factory(direction, name=''):
    def _move(tf):
        field, status = extract_data(tf)
        new_field, new_status = field.get_moved(direction)
        return new_field, (status or new_status)
    _move.__name__ = 'move_{}'.format(name)
    return _move


def maximize_score(tf):
    result = None, None
    for direction in DIRECTIONS:
        cres = move_factory(direction)(tf)
        if result[0] is None or result[0].score < cres[0].score:
            result = cres
    return result


def select_best(tf1, tf2):
    field1, status1 = extract_data(tf1)
    field2, status2 = extract_data(tf2)

    return tf1 if field1.score > field2.score else tf2


def if_equal_in_row(tf, res1, res2):
    field, status = extract_data(tf)
    return res1 if field.equal_in_row else res2


def if_equal_in_column(tf, res1, res2):
    field, status = extract_data(tf)
    return res1 if field.equal_in_column else res2


def play_game(function, field=None, callback=None):
    if field is None:
        field = Field()

    while not field.is_over:
        # field.print()
        try:
            field, status = function(field)
        except Exception as e:
            status = False

        if not status:
            for direction in DIRECTIONS:
                field, ts = move_factory(direction)(field)
                if ts:
                    break
        if callback is not None:
            callback(field)
    # print(field.score)
    return field.score


def evalSymbReg(individual):
    # print(individual)
    func = toolbox.compile(expr=individual)
    NUM = 10
    result = 0
    for i in range(NUM):
        result += play_game(func)
    return result / NUM,


def show_algo(function, gen_num):
    from game.visualize import Visualizer
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    visualizer = Visualizer(Field(), caption='Gen. {}'.format(gen_num))
    player = functools.partial(play_game, function)
    visualizer.run_bot(player)
    app.exec_()


def register_data(pset):
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=2)
    toolbox.register("individual", tools.initIterate, creator.Individual,
                     toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    toolbox.register("evaluate", evalSymbReg)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

    toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"),
                                            max_value=17))
    toolbox.decorate("mutate",
                     gp.staticLimit(key=operator.attrgetter("height"),
                                    max_value=17))


def main():
    arguments = get_arguments()
    if arguments.seed is not None:
        random.seed(arguments.seed)

    if arguments.test is not None:
        show_algo(lambda x: eval(arguments.test), 'test')
        sys.exit()

    pset = gp.PrimitiveSet("MAIN", 1)
    for direction, name in zip(DIRECTIONS, ('left', 'up', 'right', 'down',)):
        pset.addPrimitive(move_factory(direction, name), 1)

    pset.addPrimitive(if_equal_in_row, 3)
    pset.addPrimitive(if_equal_in_column, 3)
    pset.addPrimitive(select_best, 2)
    # pset.addPrimitive(maximize_score, 1)
    # pset.addPrimitive(move_left_makes_equal_in_clmn, 3)
    # pset.addPrimitive(move_left_makes_equal_in_row, 3)

    pset.renameArguments(ARG0='x')

    creator.create("FitnessMin", base.Fitness, weights=(1.0,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

    register_data(pset)

    history = tools.History()
    pop = toolbox.population(n=20)
    hof = tools.HallOfFame(1)
    history.update(pop)
    
    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats.register("avg", numpy.mean)
    mstats.register("std", numpy.std)
    mstats.register("min", numpy.min)
    mstats.register("max", numpy.max)

    pop, log = algorithms.eaSimple(pop, toolbox, 0.5, 0.1,
                                   arguments.generations, stats=mstats,
                                   halloffame=hof, verbose=True)

    best_ind = tools.selBest(pop, 1)[0]

    if arguments.preview:
        show_algo(toolbox.compile(expr=best_ind), arguments.generations)
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
    return pop, log, hof


if __name__ == "__main__":
    pop, log, hof = main()

