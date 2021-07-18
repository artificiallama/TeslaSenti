from sklearn import naive_bayes
from sklearn.model_selection import GridSearchCV, StratifiedKFold
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def grid_search_wrapper(
    model: naive_bayes.MultinomialNB, x_train: np.ndarray,
    y_train: pd.Series(dtype=float), check_params: Dict[str, List[float]],
    refit_score: str) -> Tuple[naive_bayes.MultinomialNB, pd.DataFrame]:
    """Identify best parameters amongst check_params for fitting the model.

    The model is fitted using every combination of parameter values found
    in check_params with crossvalidation. The best parameter values maximise
    the refit_score for the fitted model. The best model is returned along
    scores for each fitted model. This includes the mean and standard deviation
    of train and test scores.

    :param model: The model to be fitted
    :type  model: Instance of sklearn base class
    :param x_train: Features for fitting the model
    :type  x_train: Scipy 2d float array
    :param y_train: Targets for fitting the model
    :type  y_train: Pandas series
    :param check_params: Names and values of parameters to be searched
    :type  check_params: Dictionary
    :param refit_score: The score to be maximized
    :type  refit_score: str
    :return: The best model and  scores of all models are returned
    :rtype:  (sklearn class instance, pandas dataframe)

    """

    clf = GridSearchCV(model, param_grid=check_params,
                       refit=refit_score,
                       cv=StratifiedKFold(shuffle=True, n_splits=20),
                       return_train_score=True)

    clf.fit(x_train, y_train)

    res = pd.DataFrame(clf.cv_results_)

    print('\n\tBest performer : ')

    print('\tbest_params_ = ', clf.best_params_)
    print('\tbest_index_ = ', clf.best_index_)
    print('\tbest_score_ = ', clf.best_score_)

    return clf.best_estimator_, res
