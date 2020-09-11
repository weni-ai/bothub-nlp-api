import math
import matplotlib.pyplot as plt
import numpy as np

mocked_repository_obj = {
    "intentions": ["a", "b", "c", "d", "e"],
    "sentences": {
        "a": ["intenção A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A", "outra frase da A"],
        "b": ["intenção B", "outra frase da B", "frase 3", "frase 4", "frase 5"],
        "c": ["intenção C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C", "outra frase da C"],
        "d": ["intenção D", "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D", "outra frase da D"],
        "e": ["intenção E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E", "outra frase da E"],
    },
    "evaluate": {
        "a": ["teste A", "outra frase teste da A", "outra frase teste da A", "outra frase teste da A", "outra frase teste da A"],
        "b": ["teste B", "outra frase teste da B", "frase teste3", "frase teste4", "frase teste5"],
        "c": ["teste C", "outra frase teste da C", "outra frase teste da C", "outra frase teste da C", "outra frase teste da C"],
        "d": ["teste D", "outra frase teste da D", "outra frase teste da D", "outra frase teste da D", "outra frase teste da D", "outra frase teste da D", "outra frase teste da D"],
        "e": ["teste E", "outra frase teste da E", "outra frase teste da E", "outra frase teste da E", "outra frase teste da E", "outra frase teste da E", "outra frase teste da E"],
    }
}


def score_normal(x,  optimal):
    """
        Based on normal distribution,
        score will decay if current value is below or above target
    """
    slim_const = 2.3
    result = math.exp(-((x - optimal) ** 2) / (2 * (optimal/slim_const) ** 2))
    return result * 100


def score_cumulated(x, optimal):
    """
        Based on cumulated distribution,
        score will increase as close current value is to the target
    """
    factor = 10/optimal
    sigma_func = 1/(1 + np.exp(-(-5 + x*factor)))
    return sigma_func * 100


def plot_func(func, optimal):

    x = np.linspace(0, 2*optimal, 100)
    y = [func(n, optimal=optimal) for n in x]

    plt.plot(x, y)
    plt.plot([optimal, optimal], [0, 100])
    plt.ylabel('score')
    plt.xlabel('distance')
    plt.show()


def intentions_balance_score(intentions, sentences):

    intentions_size = len(intentions)
    if intentions_size < 2:
        return 0

    sentences_size = 0
    for intention in sentences.keys():
        sentences_size += len(sentences[intention])

    scores = []
    for intention in sentences.keys():
        this_size = len(sentences[intention])
        excl_size = sentences_size - this_size

        # Mean of sentences/intention excluding this intention
        # It is the optimal target
        excl_mean = excl_size/(intentions_size-1)
        print(this_size, excl_mean)
        scores.append(score_normal(this_size, excl_mean))

    # for score in scores:
    #     print(score)

    score = sum(scores)/len(scores)

    return {
        "score": score,
        "recommended": int(sentences_size/intentions_size)
    }


def intentions_size_score(intentions, sentences):
    intentions_size = len(intentions)
    if intentions_size < 2:
        return 0

    optimal = int(106.6556 + (19.75708 - 106.6556)/(1 + (intentions_size/8.791823)**1.898546))

    scores = []
    for intention in sentences.keys():
        this_size = len(sentences[intention])
        if this_size >= optimal:
            scores.append(1.0)
        else:
            scores.append(score_cumulated(this_size, optimal))

    score = sum(scores)/len(scores)

    return {
        "score": score,
        "recommended": optimal
    }


def evaluate_size_score(intentions, sentences, evaluate_data):
    intentions_size = len(intentions)
    if intentions_size < 2:
        return 0

    sentences_size = 0
    for intention in sentences.keys():
        sentences_size += len(sentences[intention])

    evaluate_size = 0
    for intention in evaluate_data.keys():
        evaluate_size += len(evaluate_data[intention])

    optimal = int(906866.6 + (-3.677954 - 906866.6)/(1 + (sentences_size/71299080000)**0.501674))

    if evaluate_size >= optimal:
        score = 1.0
    else:
        score = score_cumulated(evaluate_size, optimal)

    return {
        "score": score,
        "recommended": optimal
    }


# TODO: word distribution score

if __name__ == "__main__":

    # plot_func(score_cumulated, 100)
    # plot_func(score_normal, 100)

    sc = evaluate_size_score(
        mocked_repository_obj.get("intentions"),
        mocked_repository_obj.get("sentences"),
        mocked_repository_obj.get("evaluate")
    )

    print(sc["score"], sc["recommended"])
