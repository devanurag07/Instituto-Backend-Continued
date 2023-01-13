from .serializers import InstituteSerializer
from institute.models import InstituteConfiguration
from institute.models import Institute
from batch.models import StudentRequest
# Owner


def create_institute(data, owner):
    # Validation Of Data
    institute_form = InstituteSerializer(data=data)

    if (institute_form.is_valid()):
        # Saving Data
        InstituteConfiguration.objects.get_or_create(institute=institute)
        institute = institute_form.save(owner=owner)
        institute_data = InstituteSerializer(institute, many=False).data

        return {
            "created": True,
            "data": institute_data
        }

    else:
        return {
            "created": False,
            "errors": institute_form.errors,
            "data": {

            }
        }


def create_batch_requests(student, institute_code, batch_codes):
    errors = {}
    institute_list = Institute.objects.filter(
        institute_code=institute_code)

    if (institute_list.exists()):
        institute = institute_list.first()
    else:
        errors["institute"] = [
            {
                institute_code: "Institute Doesn't Exists"
            }
        ]

        return False, errors

    # Validation
    for batch_code in batch_codes:
        batch_list = institute.batches.filter(
            batch_code=batch_code)
        if (not batch_list.exists()):
            errors.setdefault('batches', [])
            errors['batches'].append({
                batch_code: "Batch Doesn't Exists"
            })

    if (len(errors.keys()) > 0):
        return False, errors
    # Validation
    for batch_code in batch_codes:
        batch = institute.batches.get(batch_code=batch_code)
        if (student not in batch.students.all()):
            StudentRequest.objects.get_or_create(batch=batch, student=student)

    return True, {}
