import unittest
from unittest.mock import MagicMock, patch

import rstr
from slicing_app.slicing import (
    extract_songs_info,
    upload_to_s3,
)

valid_line = rstr.xeger(r"\w*\d\d:\d\d:\d\d\w*")
invalid_line = rstr.xeger(r"\w*")
empty_line = " "

multiple_valid_lines = "\n".join([valid_line] * 10)
valid_invalid_lines = "\n".join([valid_line, valid_line, invalid_line])
valid_invalid_empty_lines = "\n".join([valid_line, empty_line, invalid_line])
valid_empty_lines = "\n".join([empty_line, valid_line, empty_line, valid_line])
multiple_invalid_lines = "\n".join([invalid_line, invalid_line, invalid_line])
invalid_empty_lines = "\n".join([invalid_line, empty_line, invalid_line])
multiple_empty_lines = "\n".join([empty_line, empty_line, empty_line])


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
            "slicing_app.slicing.os.environ",
            {
                "AWS_ACCESS_KEY_ID": "<access_key_id>",
                "AWS_SECRET_ACCESS_KEY": "<secret_key_access>",
                "S3_BUCKET": "<s3_bucket>",
            },
        ), patch(
            "slicing_app.slicing.Config", return_value=config
        ) as get_config:

            url = upload_to_s3(self.key, self.file)

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

    def test_boto_commands_dont_execute_when_lacking_env_vars(self):
        with patch(
            "slicing_app.slicing.boto3.resource"
        ) as resource_create, patch("slicing_app.slicing.os.environ", {}):
            self.assertRaises(
                KeyError, upload_to_s3, self.key, self.file
            )

            resource_create.assert_not_called()
