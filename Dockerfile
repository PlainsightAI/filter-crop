FROM us-west1-docker.pkg.dev/plainsightai-prod/oci/filter_base:python-3.11

CMD ["python", "-m", "filter_crop.filter"]
