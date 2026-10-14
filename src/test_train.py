from unittest.mock import MagicMock

def make_mock_results(mAP50:float=0.75, save_dir:str|None=None):
    """Creates a mock YOLO results object for testing.

        Builds a `MagicMock` populated with a `results_dict` containing
        typical YOLO metrics (mAP50, mAP50-95, precision, recall) and a
        `save_dir` attribute, so it can stand in for a real training/
        validation results object in tests.

        Args:
            mAP50 (float): The mAP50 metric value to use. `mAP50-95` is
                derived as `mAP50 * 0.6`. Defaults to 0.75.
            save_dir (str | None): The mock save directory path. Defaults
                to '/fake/runs/detect/train1' if not provided.

        Returns:
            MagicMock: A mock results object with `results_dict` and
            `save_dir` attributes set.
        """
    results = MagicMock()
    results.results_dict = {
        'metrics/mAP50(B)':    mAP50,
        'metrics/mAP50-95(B)': mAP50 * 0.6,
        'metrics/precision(B)': 0.8,
        'metrics/recall(B)':    0.7,
    }
    results.save_dir = save_dir or '/fake/runs/detect/train1'
    return results


#def make_mock_yolo(mAP50:float=0.75, save_dir:str='/fake/runs/detect/train1'):
#    """Returns a mock YOLO class whose .train() returns fake results."""
#    mock_model = create_autospec(RealModelClass, instance=True)
#    mock_model.train.return_value = make_mock_results(mAP50, save_dir))
#    MockYOLO = MagicMock(return_value=mock_model)
#    return MockYOLO, mock_model
