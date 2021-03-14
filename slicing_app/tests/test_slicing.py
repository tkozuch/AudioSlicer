import datetime
import unittest
from unittest.mock import MagicMock, call, patch

from slicing_app.slicing import (
    AudioLoadError,
    EnvVarsMissingError,
    slice_audio,
    upload_to_s3
)

ENV_VARIABLES_MOCK = {
    "AWS_ACCESS_KEY_ID": "<access_key_id>",
    "AWS_SECRET_ACCESS_KEY": "<secret_key_access>",
    "S3_BUCKET": "<s3_bucket>",
}


class TestUploadToS3(unittest.TestCase):
    def setUp(self) -> None:
        self.key = "key-mock"
        self.file = "file-mock"

    def test_executes_appropriate_boto_commands(self):
        boto_resource = MagicMock()
        config = MagicMock()

        with patch(
            "slicing_app.slicing.boto3.resource", return_value=boto_resource
        ) as resource_create, patch(
            "slicing_app.slicing.os.environ", ENV_VARIABLES_MOCK
        ), patch(
            "slicing_app.slicing.Config", return_value=config
        ) as get_config:

            url = upload_to_s3(self.key, self.file, *ENV_VARIABLES_MOCK.values())

            get_config.assert_called_with(signature_version="s3v4")
            resource_create.assert_called_with(
                "s3",
                aws_access_key_id="<access_key_id>",
                aws_secret_access_key="<secret_key_access>",
                config=config,
            )
            boto_resource.Bucket.assert_called_with("<s3_bucket>")
            boto_resource.Bucket.return_value.put_object.assert_called_with(
                Key=self.key, Body=self.file, ACL="public-read"
            )

            self.assertEqual(
                url,
                "https://s3.eu-central-1.amazonaws.com/{}/{}".format(
                    "<s3_bucket>", self.key
                ),
            )


class TestSliceAudio(unittest.TestCase):
    def setUp(self) -> None:
        self.file_mock = MagicMock()
        self.text_input_mock = MagicMock()

        self.text_input_1 = {
            "zero fragment title": datetime.time(0, 0, 25),
            "first fragment title": datetime.time(1, 0, 10),
            "second fragment title": datetime.time(1, 15, 0),
            "third fragment title": datetime.time(2, 25, 0),
        }
        self.files_names_1 = [
            "zero_fragment_title.mp3",
            "first_fragment_title.mp3",
            "second_fragment_title.mp3",
            "third_fragment_title.mp3",
        ]
        self.audio_fragments_1 = [MagicMock() for _ in range(len(self.text_input_1))]

    def test_raises_audio_error_when_problem_with_loading_audio(self):
        with patch("slicing_app.slicing.AudioSegment.from_mp3", side_effect=Exception):
            self.assertRaises(
                AudioLoadError, slice_audio, self.file_mock, self.text_input_mock
            )

    @patch("slicing_app.slicing.upload_to_s3")
    @patch("slicing_app.slicing.load_audio")
    @patch("slicing_app.slicing.update_task_progress")
    @patch("slicing_app.slicing.os.environ", ENV_VARIABLES_MOCK)
    @patch("slicing_app.slicing.divide_audio")
    @patch("slicing_app.slicing.get_file_name")
    def test_upload_to_s3_called_with_appropriate_args(
        self,
        get_file_name,
        divide_audio,
        update_task_progress,
        load_audio,
        upload_to_s3_mock,
    ):
        get_file_name.side_effect = self.files_names_1
        divide_audio.return_value = self.audio_fragments_1

        slice_audio(self.file_mock, self.text_input_1)

        self.assertEqual(
            [
                call(
                    self.files_names_1[0],
                    self.audio_fragments_1[0].export(format="mp3", bitrate="202"),
                    *ENV_VARIABLES_MOCK.values()
                ),
                call(
                    self.files_names_1[1],
                    self.audio_fragments_1[1].export(format="mp3", bitrate="202"),
                    *ENV_VARIABLES_MOCK.values()
                ),
                call(
                    self.files_names_1[2],
                    self.audio_fragments_1[2].export(format="mp3", bitrate="202"),
                    *ENV_VARIABLES_MOCK.values()
                ),
                call(
                    self.files_names_1[3],
                    self.audio_fragments_1[3].export(format="mp3", bitrate="202"),
                    *ENV_VARIABLES_MOCK.values()
                ),
            ],
            upload_to_s3_mock.call_args_list,
        )

    @patch("slicing_app.slicing.upload_to_s3")
    @patch("slicing_app.slicing.load_audio")
    @patch("slicing_app.slicing.update_task_progress")
    @patch("slicing_app.slicing.os.environ", ENV_VARIABLES_MOCK)
    @patch("slicing_app.slicing.divide_audio")
    @patch("slicing_app.slicing.get_file_name")
    def test_update_task_progress_called_with_appropriate_args(
        self,
        get_file_name,
        divide_audio,
        update_task_progress,
        load_audio,
        upload_to_s3_mock,
    ):
        slice_audio(self.file_mock, self.text_input_1)

        self.assertEqual(
            [
                call(part=1, of_parts=len(self.text_input_1)),
                call(part=2, of_parts=len(self.text_input_1)),
                call(part=3, of_parts=len(self.text_input_1)),
                call(part=4, of_parts=len(self.text_input_1)),
            ],
            update_task_progress.call_args_list,
        )

    @patch("slicing_app.slicing.upload_to_s3")
    @patch("slicing_app.slicing.load_audio")
    @patch("slicing_app.slicing.update_task_progress")
    @patch("slicing_app.slicing.os.environ", ENV_VARIABLES_MOCK)
    @patch("slicing_app.slicing.divide_audio")
    @patch("slicing_app.slicing.get_file_name")
    def test_returns_urls_and_files_names(
        self,
        get_file_name,
        divide_audio,
        update_task_progress,
        load_audio,
        upload_to_s3_mock,
    ):
        upload_to_s3_mock.side_effect = ["url_1", "url_2", "url_3", "url_4"]
        get_file_name.side_effect = self.files_names_1

        result = slice_audio(self.file_mock, self.text_input_1)

        self.assertEqual(
            {
                "urls": ["url_1", "url_2", "url_3", "url_4"],
                "files_names": self.files_names_1,
            },
            result,
        )

    @patch("slicing_app.slicing.upload_to_s3")
    @patch("slicing_app.slicing.load_audio")
    @patch("slicing_app.slicing.update_task_progress")
    @patch("slicing_app.slicing.os.environ", ENV_VARIABLES_MOCK)
    @patch("slicing_app.slicing.divide_audio")
    @patch("slicing_app.slicing.get_file_name")
    def test_upload_to_s3_and_update_task_functions_arent_executed_when_empty_text_input(
        self,
        get_file_name,
        divide_audio,
        update_task_progress,
        load_audio,
        upload_to_s3_mock,
    ):
        slice_audio(self.file_mock, text_input={})

        upload_to_s3_mock.assert_not_called()
        update_task_progress.assert_not_called()

    @patch("slicing_app.slicing.upload_to_s3")
    @patch("slicing_app.slicing.load_audio")
    @patch("slicing_app.slicing.update_task_progress")
    @patch("slicing_app.slicing.os.environ", {})
    @patch("slicing_app.slicing.divide_audio")
    @patch("slicing_app.slicing.get_file_name")
    def test_doesnt_call_upload_when_missing_env_vars(
        self,
        get_file_name,
        divide_audio,
        update_task_progress,
        load_audio,
        upload_to_s3_mock,
    ):
        self.assertRaises(
            EnvVarsMissingError, slice_audio, self.file_mock, self.text_input_1
        )

        upload_to_s3_mock.assert_not_called()
