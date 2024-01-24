import hashlib
import logging

import aiohttp
import cloudinary
import cloudinary.uploader
from cloudinary.uploader import upload
from fastapi import APIRouter
from concurrent.futures import ThreadPoolExecutor

from src.conf.config import config

cloud_router = APIRouter(prefix='/cloudinary')

# пул потоків
thread_pool_executor = ThreadPoolExecutor()


class CloudinaryService:
    cloudinary.config(
        cloud_name=config.CLOUDINARY_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET,
        secure=True,
    )

    @staticmethod
    @cloud_router.post("/transform-image")
    async def transform_image(image: bytes):
        """
        The transform_image function takes an image as a byte stream and uploads it to Cloudinary.
        It then transforms the uploaded image by resizing it to 100x50 pixels, and returns the URL of
        the transformed image.

        :param image: bytes: Pass the image data to the function
        :return: A dictionary with a single key, transformed_image_url
        :doc-author: Trelent
        """
        original_image = await cloudinary.uploader.upload(image)

        transformed_image = await cloudinary.uploader.upload(
            original_image["url"],
            width=100,
            height=50,
            public_id=original_image["public_id"] + "_transformed"
        )

        # Отримання URL-адреси трансформованого зображення.
        transformed_image_url = transformed_image["secure_url"]

        return {"transformed_image_url": transformed_image_url}

    # Асинхронна функція завантаження та трансформації зображення
    @classmethod
    async def upload_and_transform_image_async(cls, image_url, transformation_params):
        """
        The upload_and_transform_image_async function takes an image URL and a transformation parameter dictionary as input.
        It then uploads the image to Cloudinary, applies the transformations specified in the transformation_params dictionary,
        and returns a new URL for accessing that transformed version of the image.

        :param cls: Pass the class name to the function
        :param image_url: Specify the url of the image to be uploaded
        :param transformation_params: Transform the image
        :return: A coroutine object
        :doc-author: Trelent
        """
        try:
            result = await upload(
                image_url,
                transformation=transformation_params
            )
            return result['url']
        except Exception as e:
            raise e

    @staticmethod
    def generate_public_id_by_email(email: str, app_name: str = config.CLOUDINARY_NAME) -> str:
        """
        The generate_public_id_by_email function takes an email address and returns a public_id for the Cloudinary API.
        The function uses the SHA-224 hash algorithm to generate a 16 character string from the email address, which is then
        used as part of a public_id in this format: {app_name}/publication/{hash}. The app name is set in config.py.

        :param email: str: Generate the public_id
        :param app_name: str: Specify the cloudinary account name
        :return: A string that is a combination of the app name and publication/name
        :doc-author: Trelent
        """
        try:
            name = hashlib.sha224(email.encode("utf-8")).hexdigest()[:16]
            return f"{app_name}/publication/{name}"
        except Exception as e:
            logging.error(f"Error generating public_id: {e}")
            raise

    @staticmethod
    async def upload_async(file_content, public_id: str, folder="publication"):
        """
        The upload_async function uploads a file to Cloudinary.

        :param file_content: Pass the file content to the function
        :param public_id: str: Specify the name of the file to be uploaded
        :param folder: Specify the folder in which to store the file on cloudinary
        :return: A dictionary with the following structure:
        :doc-author: Trelent
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Відправка файлу на сервер Cloudinary
                async with session.post(
                        f"https://api.cloudinary.com/v1_1/{config.CLOUDINARY_NAME}/upload",
                        data={"file": file_content, "public_id": public_id, "overwrite": "true"},
                ) as response:
                    return await response.json()
        except Exception as e:
            logging.error(f"Error uploading file to Cloudinary: {e}")
            raise

    @staticmethod
    def generate_url(r, public_id) -> str:
        """
        The generate_url function takes in a request and public_id,
        and returns a URL for the image. The function uses the CloudinaryImage class to build
        the URL with parameters such as width, height, crop type (fill), and version.

        :param r: Get the version of the image
        :param public_id: Identify the image in cloudinary
        :return: A url for the image
        :doc-author: Trelent
        """
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url

    @staticmethod
    def upload_image(image_data: bytes, public_id: str):
        """
        The upload_image function takes in a request and public_id, and returns a URL for the image.
        :param image_data: Specify the url of the image to be uploaded
        :param public_id: Identify the image in cloudinary
        :return:
        """

        return cloudinary.uploader.upload(
            image_data,
            public_id=public_id,
            overwrite=True,
            folder="transformed_images"
        )
