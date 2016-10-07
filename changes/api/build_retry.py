import uuid

from flask.ext.restful import reqparse
from flask_restful.types import boolean
from sqlalchemy.orm import joinedload

from changes.api.base import APIView
from changes.api.build_index import create_build
from changes.config import db
from changes.constants import Cause, SelectiveTestingPolicy
from changes.models.build import Build
from changes.models.buildmessage import BuildMessage
from changes.utils.selective_testing import get_selective_testing_policy


class BuildRetryAPIView(APIView):
    parser = reqparse.RequestParser()

    """Optional flag, default to False."""
    parser.add_argument('selective_testing', type=boolean, default=False)

    def post(self, build_id):
        args = self.parser.parse_args()

        build = Build.query.options(
            joinedload('project', innerjoin=True),
            joinedload('author'),
            joinedload('source').joinedload('revision'),
        ).get(build_id)
        if build is None:
            return '', 404

        selective_testing_policy = SelectiveTestingPolicy.disabled
        build_message = None
        if args.selective_testing:
            if not build.source.patch:
                selective_testing_policy, reasons = get_selective_testing_policy(build.project, build.source.revision_sha, None)
                if reasons:
                    if selective_testing_policy is SelectiveTestingPolicy.disabled:
                        reasons = ["Selective testing was requested but not done because:"] + ['    ' + m for m in reasons]
                    build_message = '\n'.join(reasons)
            else:
                # NOTE: for diff builds, it makes sense to just do selective testing,
                # since it will never become a parent build and will never be used to
                # calculate revision results.
                selective_testing_policy = SelectiveTestingPolicy.enabled

        collection_id = uuid.uuid4()
        new_build = create_build(
            project=build.project,
            collection_id=collection_id,
            label=build.label,
            target=build.target,
            message=build.message,
            author=build.author,
            source=build.source,
            cause=Cause.retry,
            selective_testing_policy=selective_testing_policy,
        )

        if build_message:
            message = BuildMessage(
                build=new_build,
                text=build_message,
            )
            db.session.add(message)
            db.session.commit()

        return '', 302, {'Location': '/api/0/builds/{0}/'.format(new_build.id.hex)}
