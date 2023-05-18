# -*- coding: utf-8 -*-
"""Unit tests for all time series regressors."""

__author__ = ["mloning", "TonyBagnall", "fkiraly", "DavidGuijo-Rubio"]


import numpy as np
import pytest

from aeon.datasets import load_cardano_sentiment, load_covid_3month
from aeon.datatypes import check_is_scitype
from aeon.regression.tests._expected_outputs import (
    cardano_sentiment_preds,
    covid_3month_preds,
)
from aeon.tests.test_all_estimators import BaseFixtureGenerator, QuickTester
from aeon.utils._testing.estimator_checks import _assert_array_almost_equal
from aeon.utils._testing.scenarios_classification import (
    ClassifierFitPredictMultivariate,
)


class RegressorFixtureGenerator(BaseFixtureGenerator):
    """Fixture generator for regression tests.

    Fixtures parameterized
    ----------------------
    estimator_class: estimator inheriting from BaseObject
        ranges over estimator classes not excluded by EXCLUDE_ESTIMATORS, EXCLUDED_TESTS
    estimator_instance: instance of estimator inheriting from BaseObject
        ranges over estimator classes not excluded by EXCLUDE_ESTIMATORS, EXCLUDED_TESTS
        instances are generated by create_test_instance class method
    scenario: instance of TestScenario
        ranges over all scenarios returned by retrieve_scenarios
    """

    # note: this should be separate from TestAllRegressors
    #   additional fixtures, parameters, etc should be added here
    #   TestAllRegressors should contain the tests only

    estimator_type_filter = "regressor"


class TestAllRegressors(RegressorFixtureGenerator, QuickTester):
    """Module level tests for all aeon regressors."""

    def test_multivariate_input_exception(self, estimator_instance):
        """Test univariate regressors raise exception on multivariate X."""
        # check if multivariate input raises error for univariate regressors

        # if handles multivariate, no error is to be raised
        #   that classifier works on multivariate data is tested in test_all_estimators
        if estimator_instance.get_tag("capability:multivariate"):
            return None

        error_msg = "multivariate series"

        # we can use the classifier scenario for multivariate regressors
        #   because the classifier scenario y is float
        scenario = ClassifierFitPredictMultivariate()

        # check if estimator raises appropriate error message
        #   composites will raise a warning, non-composites an exception
        if estimator_instance.is_composite():
            with pytest.warns(UserWarning, match=error_msg):
                scenario.run(estimator_instance, method_sequence=["fit"])
        else:
            with pytest.raises(ValueError, match=error_msg):
                scenario.run(estimator_instance, method_sequence=["fit"])

    def test_regressor_output(self, estimator_instance, scenario):
        """Test regressor outputs the correct data types and values.

        Test predict produces a np.array or pd.Series with only values seen in the train
        data, and that predict_proba probability estimates add up to one.
        """
        X_new = scenario.args["predict"]["X"]
        # we use check_is_scitype to get the number instances in X_new
        #   this is more robust against different scitypes in X_new
        _, _, X_new_metadata = check_is_scitype(X_new, "Panel", return_metadata=True)
        X_new_instances = X_new_metadata["n_instances"]

        # run fit and predict
        y_pred = scenario.run(estimator_instance, method_sequence=["fit", "predict"])

        # check predict
        assert isinstance(y_pred, np.ndarray)
        assert y_pred.shape == (X_new_instances,)
        assert np.issubdtype(y_pred.dtype, np.floating)

    def test_regressor_on_covid_3month_data(self, estimator_class):
        """Test regressor on unit test data."""
        # we only use the first estimator instance for testing
        classname = estimator_class.__name__

        # retrieve expected preds output, and skip test if not available
        if classname in covid_3month_preds.keys():
            expected_preds = covid_3month_preds[classname]
        else:
            # skip test if no expected probas are registered
            return None
        # we only use the first estimator instance for testing
        estimator_instance = estimator_class.create_test_instance(
            parameter_set="results_comparison"
        )
        # set random seed if possible
        if "random_state" in estimator_instance.get_params().keys():
            estimator_instance.set_params(random_state=0)

        # load Covid3Month data
        X_train, y_train = load_covid_3month(split="train")
        X_test, y_test = load_covid_3month(split="test")
        indices_train = np.random.RandomState(0).choice(len(y_train), 10, replace=False)
        indices_test = np.random.RandomState(0).choice(len(y_test), 10, replace=False)

        # train regressor and predict
        estimator_instance.fit(X_train[indices_train], y_train[indices_train])
        y_preds = estimator_instance.predict(X_test[indices_test])

        # assert predictions are the same
        _assert_array_almost_equal(y_preds, expected_preds, decimal=4)

    def test_regressor_on_cardano_sentiment(self, estimator_class):
        """Test regressor on cardano sentiment data."""
        # we only use the first estimator instance for testing
        classname = estimator_class.__name__

        # retrieve expected preds output, and skip test if not available
        if classname in cardano_sentiment_preds.keys():
            expected_preds = cardano_sentiment_preds[classname]
        else:
            # skip test if no expected preds are registered
            return None

        # we only use the first estimator instance for testing
        estimator_instance = estimator_class.create_test_instance(
            parameter_set="results_comparison"
        )
        # set random seed if possible
        if "random_state" in estimator_instance.get_params().keys():
            estimator_instance.set_params(random_state=0)

        # load unit test data
        X_train, y_train = load_cardano_sentiment(split="train")
        X_test, y_test = load_cardano_sentiment(split="test")

        indices_train = np.random.RandomState(4).choice(len(y_train), 10, replace=False)
        indices_test = np.random.RandomState(4).choice(len(y_test), 10, replace=False)

        # train regressor and predict
        estimator_instance.fit(X_train[indices_train], y_train[indices_train])
        y_preds = estimator_instance.predict(X_test[indices_test])

        # assert predictions are the same
        _assert_array_almost_equal(y_preds, expected_preds, decimal=4)