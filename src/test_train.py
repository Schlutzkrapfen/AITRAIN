from unittest.mock import MagicMock, patch, mock_open, call
def make_mock_results(mAP50=0.75, save_dir=None):
    """Returns a mock YOLO results object."""
    results = MagicMock()
    results.results_dict = {
        'metrics/mAP50(B)':    mAP50,
        'metrics/mAP50-95(B)': mAP50 * 0.6,
        'metrics/precision(B)': 0.8,
        'metrics/recall(B)':    0.7,
    }
    results.save_dir = save_dir or '/fake/runs/detect/train1'
    return results
 
 
def make_mock_yolo(mAP50=0.75, save_dir='/fake/runs/detect/train1'):
    """Returns a mock YOLO class whose .train() returns fake results."""
    mock_model = MagicMock()
    mock_model.train.return_value = make_mock_results(mAP50, save_dir)
    MockYOLO = MagicMock(return_value=mock_model)
    return MockYOLO, mock_model
