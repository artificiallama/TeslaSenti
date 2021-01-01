from sklearn.model_selection import GridSearchCV, StratifiedKFold
import pandas as pd

# Figure out best parameters amongst check_params for model so that
# refit_score is maximized.


def grid_search_wrapper(model, x_train, y_train, check_params, refit_score):

    clf = GridSearchCV(model, param_grid=check_params,
                       refit=refit_score,
                       cv=StratifiedKFold(shuffle=True, n_splits=20),
                       return_train_score=True)

    clf.fit(x_train, y_train)

    res = pd.DataFrame(clf.cv_results_)

    print('\n\tBest performer :')

    print('\tbest_params_ = ', clf.best_params_)
    print('\tbest_index_ = ', clf.best_index_)
    print('\tbest_score_ = ', clf.best_score_)

    return clf.best_estimator_, res
