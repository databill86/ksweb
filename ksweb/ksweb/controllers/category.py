# -*- coding: utf-8 -*-
"""Category controller module"""
from bson import ObjectId
from tg import decode_params
from tg import expose, validate, RestController, validation_errors_response
from ksweb import model
from ksweb.lib.validator import CategoryExistValidator
from tg import flash
from tg import request
from tw2.core import StringLengthValidator


class CategoryController(RestController):
    # Uncomment this line if your controller requires an authenticated user
    # allow_only = predicates.not_anonymous()

    @expose('json')
    @validate({
        'id': CategoryExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def get_one(self, id, **kw):
        qa = model.Category.query.get(_id=ObjectId(id))
        return dict(qa=qa)

    @expose('json')
    def get_all(self):
        categories = model.Category.query.find({'visible': True}).all()
        return dict(categories=categories)

    @decode_params('json')
    @expose('json')
    @validate({
        'workspace_name': StringLengthValidator(min=2),
    }, error_handler=validation_errors_response)
    def create(self, workspace_name=None, **kw):
        workspace = model.Category(
            visible=True,
            name=str(workspace_name)
        )
        flash("Category successfully created!")
        return dict(workspaces=self.get_all())

    @decode_params('json')
    @expose('json')
    @validate({
        'workspace_id': CategoryExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def delete(self, method=None, workspace_id=None, **kw):
        qa = model.Qa.query.remove({'_category': ObjectId(workspace_id)})
        o = model.Output.query.remove({'_category': ObjectId(workspace_id)})
        p = model.Precondition.query.remove({'_category': ObjectId(workspace_id)})
        doc = [document._id for document in model.Document.query.find({'_category': ObjectId(workspace_id)}).all()]
        q = model.Questionary.query.remove({'_document': {'$in': doc}})
        q = model.Document.query.remove({'_id': {'$in': doc}})
        ws = model.Category.query.remove({'_id': ObjectId(workspace_id)})
        flash("Category and all entities associated deleted")
        return dict(workspaces=self.get_all())
