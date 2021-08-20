from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Union

from fastapi import \
    Depends, \
    Response
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request


class RouteResourceBse(ABC):
    @abstractmethod
    def find_one(self, api,
                 *,
                 path,
                 query_service,
                 parsing_service,
                 async_mode,
                 response_model,
                 dependencies,
                 request_url_param_model,
                 request_query_model,
                 db_session):
        raise NotImplementedError

    @abstractmethod
    def find_many(self,
                  api, *,
                  query_service,
                  parsing_service,
                  async_mode,
                  path,
                  response_model,
                  dependencies,
                  request_query_model,
                  db_session):
        raise NotImplementedError

    @abstractmethod
    def upsert_one(api, *,
                   path,
                   query_service,
                   parsing_service,
                   async_mode,
                   response_model,
                   request_body_model,
                   dependencies,
                   db_session,
                   unique_list):
        raise NotImplementedError

    @abstractmethod
    def upsert_many(api, *,
                    query_service,
                    parsing_service,
                    async_mode,
                    path,
                    response_model,
                    dependencies,
                    request_body_model,
                    db_session,
                    unique_list):
        raise NotImplementedError

    @abstractmethod
    def delete_one(api, *,
                   query_service,
                   parsing_service,
                   async_mode,
                   path,
                   response_model,
                   dependencies,
                   request_query_model,
                   request_url_model,
                   db_session, ):
        raise NotImplementedError

    @abstractmethod
    def delete_many(api, *,
                    query_service,
                    parsing_service,
                    async_mode,
                    path,
                    response_model,
                    dependencies,
                    request_query_model,
                    db_session):
        raise NotImplementedError

    @abstractmethod
    def post_redirect_get(api, *,
                          dependencies,
                          request_body_model,
                          db_session,
                          crud_service,
                          result_parser,
                          async_mode,
                          response_model):
        raise NotImplementedError

    @abstractmethod
    def patch_one(api, *,
                  path,
                  response_model,
                  dependencies,
                  request_url_param_model,
                  request_body_model,
                  request_query_model,
                  db_session,
                  crud_service,
                  result_parser,
                  async_mode):
        raise NotImplementedError

    @abstractmethod
    def patch_many(api, *,
                   path,
                   response_model,
                   dependencies,
                   request_body_model,
                   request_query_model,
                   db_session,
                   crud_service,
                   result_parser,
                   async_mode):
        raise NotImplementedError

    @abstractmethod
    def put_one(api, *,
                path,
                request_url_param_model,
                request_body_model,
                response_model,
                dependencies,
                request_query_model,
                db_session,
                crud_service,
                result_parser,
                async_mode):
        raise NotImplementedError

    @abstractmethod
    def put_many(api, *,
                 path,
                 response_model,
                 dependencies,
                 request_query_model,
                 request_body_model,
                 db_session,
                 crud_service,
                 result_parser,
                 async_mode):
        raise NotImplementedError


class SQLALChemyBaseRouteSource(RouteResourceBse):

    @classmethod
    def find_one(self, api,
                 *,
                 path,
                 query_service,
                 parsing_service,
                 execute_service,
                 async_mode,
                 response_model,
                 dependencies,
                 request_url_param_model,
                 request_query_model,
                 db_session):

        if not async_mode:
            @api.get(path, status_code=200, response_model=response_model, dependencies=dependencies)
            def get_one_by_primary_key(response: Response,
                                       request: Request,
                                       url_param=Depends(request_url_param_model),
                                       query=Depends(request_query_model),
                                       session=Depends(db_session)):
                stmt = query_service.get_one(filter_args=query,
                                             extra_args=url_param,
                                             request_obj=request,
                                             session=session)
                query_result = execute_service.get_one(session, stmt)
                response_result = parsing_service.find_one(response_model=response_model,
                                                           sql_execute_result=query_result,
                                                           fastapi_response=response,
                                                           session=session)
                return response_result
        else:
            @api.get(path, status_code=200, response_model=response_model, dependencies=dependencies)
            async def async_get_one_by_primary_key(response: Response,
                                                   request: Request,
                                                   url_param=Depends(request_url_param_model),
                                                   query=Depends(request_query_model),
                                                   session=Depends(db_session)):
                stmt = query_service.get_one(filter_args=query,
                                                   extra_args=url_param,
                                                   request_obj=request,
                                                   session=session)
                query_result = await execute_service.async_get_one(session, stmt)

                response_result = await parsing_service.async_find_one(response_model=response_model,
                                                                       sql_execute_result=query_result,
                                                                       fastapi_response=response,
                                                                       session=session)
                return response_result

    @classmethod
    def find_many(self, api, *,
                  query_service,
                  parsing_service,
                  async_mode,
                  path,
                  response_model,
                  dependencies,
                  request_query_model,
                  db_session):

        if async_mode:
            @api.get(path, response_model=response_model, dependencies=dependencies)
            async def async_get_many(response: Response,
                                     request: Request,
                                     query=Depends(request_query_model),
                                     session=Depends(
                                         db_session)
                                     ):
                query_result = await query_service.async_get_many(query=query,
                                                                  session=session,
                                                                  request_obj=request)

                parsed_response = await parsing_service.async_find_many(response_model=response_model,
                                                                        sql_execute_result=query_result,
                                                                        fastapi_response=response,
                                                                        session=session)
                return parsed_response
        else:
            @api.get(path, response_model=response_model, dependencies=dependencies)
            def get_many(response: Response,
                         request: Request,
                         query=Depends(request_query_model),
                         session=Depends(
                             db_session)
                         ):
                query_result = query_service.get_many(query=query,
                                                      session=session,
                                                      request_obj=request)

                parsed_response = parsing_service.find_manyp(response_model=response_model,
                                                             sql_execute_result=query_result,
                                                             fastapi_response=response,
                                                             session=session)
                return parsed_response

    @classmethod
    def upsert_one(self, api, *,
                   path,
                   query_service,
                   parsing_service,
                   async_mode,
                   response_model,
                   request_body_model,
                   dependencies,
                   db_session,
                   unique_list):
        if async_mode:

            @api.post(path, status_code=201, response_model=response_model, dependencies=dependencies)
            async def async_insert_one_and_support_upsert(
                    response: Response,
                    request: Request,
                    query: request_body_model = Depends(request_body_model),
                    session=Depends(db_session)
            ):
                try:
                    query_result = await query_service.async_upsert(insert_arg=query,
                                                                    unique_fields=unique_list,
                                                                    session=session,
                                                                    request_obj=request)
                except IntegrityError as e:
                    err_msg, = e.orig.args
                    if 'duplicate key value violates unique constraint' not in err_msg:
                        raise e
                    result = Response(status_code=HTTPStatus.CONFLICT)
                    return result
                return await parsing_service.async_upsert_one(response_model=response_model,
                                                              sql_execute_result=query_result,
                                                              fastapi_response=response,
                                                              session=session)
        else:

            @api.post(path, status_code=201, response_model=response_model, dependencies=dependencies)
            def insert_one_and_support_upsert(
                    response: Response,
                    request: Request,
                    query: request_body_model = Depends(request_body_model),
                    session=Depends(db_session)
            ):
                try:
                    query_result = query_service.upsert(insert_arg=query,
                                                        unique_fields=unique_list,
                                                        session=session,
                                                        request_obj=request)
                except IntegrityError as e:
                    err_msg, = e.orig.args
                    if 'duplicate key value violates unique constraint' not in err_msg:
                        raise e
                    result = Response(status_code=HTTPStatus.CONFLICT)
                    return result
                return parsing_service.upsert_one(response_model=response_model,
                                                  sql_execute_result=query_result,
                                                  fastapi_response=response,
                                                  session=session)

    @classmethod
    def upsert_many(self, api, *,
                    query_service,
                    parsing_service,
                    async_mode,
                    path,
                    response_model,
                    dependencies,
                    request_body_model,
                    db_session,
                    unique_list):

        if async_mode:
            @api.post(path, status_code=201, response_model=response_model, dependencies=dependencies)
            async def async_insert_many_and_support_upsert(
                    response: Response,
                    request: Request,
                    query: request_body_model = Depends(request_body_model),
                    session=Depends(db_session)
            ):
                try:
                    query_result = await query_service.upsert(insert_arg=query,
                                                              unique_fields=unique_list,
                                                              session=session,
                                                              upsert_one=False,
                                                              request_obj=request)
                except IntegrityError as e:
                    err_msg, = e.orig.args
                    if 'duplicate key value violates unique constraint' not in err_msg:
                        raise e
                    result = Response(status_code=HTTPStatus.CONFLICT)
                    return result

                return await parsing_service.async_upsert_many(response_model=response_model,
                                                               sql_execute_result=query_result,
                                                               fastapi_response=response,
                                                               session=session)
        else:
            @api.post(path, status_code=201, response_model=response_model, dependencies=dependencies)
            def insert_many_and_support_upsert(
                    response: Response,
                    request: Request,
                    query: request_body_model = Depends(request_body_model),
                    session=Depends(db_session)
            ):
                try:
                    query_result = query_service.async_upsert(insert_arg=query,
                                                              unique_fields=unique_list,
                                                              session=session,
                                                              upsert_one=False,
                                                              request_obj=request)
                except IntegrityError as e:
                    err_msg, = e.orig.args
                    if 'duplicate key value violates unique constraint' not in err_msg:
                        raise e
                    result = Response(status_code=HTTPStatus.CONFLICT)
                    return result

                return parsing_service.async_upsert_many(response_model=response_model,
                                                         sql_execute_result=query_result,
                                                         fastapi_response=response,
                                                         session=session)

    @classmethod
    def delete_one(self, api, *,
                   query_service,
                   parsing_service,
                   async_mode,
                   path,
                   response_model,
                   dependencies,
                   request_query_model,
                   request_url_model,
                   db_session, ):

        if async_mode:
            @api.delete(path, status_code=200, response_model=response_model, dependencies=dependencies)
            async def async_delete_one_by_primary_key(response: Response,
                                                      request: Request,
                                                      query=Depends(request_query_model),
                                                      request_url_param_model=Depends(request_url_model),
                                                      session=Depends(db_session)):
                query_result = await query_service.async_delete(primary_key=request_url_param_model,
                                                                delete_args=query,
                                                                session=session,
                                                                request_obj=request)

                return await parsing_service.async_delete_one(response_model=response_model,
                                                              sql_execute_result=query_result,
                                                              fastapi_response=response,
                                                              session=session)
        else:
            @api.delete(path, status_code=200, response_model=response_model, dependencies=dependencies)
            def delete_one_by_primary_key(response: Response,
                                          request: Request,
                                          query=Depends(request_query_model),
                                          request_url_param_model=Depends(request_url_model),
                                          session=Depends(db_session)):
                query_result = query_service.delete(primary_key=request_url_param_model,
                                                    delete_args=query,
                                                    session=session,
                                                    request_obj=request)

                return parsing_service.delete_one(response_model=response_model,
                                                  sql_execute_result=query_result,
                                                  fastapi_response=response,
                                                  session=session)

    @classmethod
    def delete_many(self, api, *,
                    query_service,
                    parsing_service,
                    async_mode,
                    path,
                    response_model,
                    dependencies,
                    request_query_model,
                    db_session):
        if async_mode:
            @api.delete(path, status_code=200, response_model=response_model, dependencies=dependencies)
            async def async_delete_many_by_query(response: Response,
                                                 request: Request,
                                                 query=Depends(request_query_model),
                                                 session=Depends(db_session)):
                query_result = await  query_service.async_delete(delete_args=query,
                                                                 session=session,
                                                                 request_obj=request)

                return await parsing_service.async_delete_many(response_model=response_model,
                                                               sql_execute_result=query_result,
                                                               fastapi_response=response,
                                                               session=session)
        else:

            @api.delete(path, status_code=200, response_model=response_model, dependencies=dependencies)
            def delete_many_by_query(response: Response,
                                     request: Request,
                                     query=Depends(request_query_model),
                                     session=Depends(db_session)):
                query_result = query_service.delete(delete_args=query,
                                                    session=session,
                                                    request_obj=request)

                return parsing_service.delete_many(response_model=response_model,
                                                   sql_execute_result=query_result,
                                                   fastapi_response=response,
                                                   session=session)

    @classmethod
    def post_redirect_get(self, api, *,
                          dependencies,
                          request_body_model,
                          db_session,
                          crud_service,
                          result_parser,
                          async_mode,
                          response_model):
        if async_mode:
            @api.post("", status_code=303, response_class=Response, dependencies=dependencies)
            async def async_create_one_and_redirect_to_get_one_api_with_primary_key(
                    request: Request,
                    insert_args: request_body_model = Depends(),
                    session=Depends(db_session),
            ):

                try:
                    query_result = await crud_service.async_insert_one(insert_args=insert_args, session=session)

                except IntegrityError as e:
                    err_msg, = e.orig.args
                    if 'duplicate key value violates unique constraint' not in err_msg:
                        raise e
                    result = Response(status_code=HTTPStatus.CONFLICT)
                    return result

                return await result_parser.async_post_redirect_get(response_model=response_model,
                                                                   sql_execute_result=query_result,
                                                                   fastapi_request=request,
                                                                   session=session)
        else:
            @api.post("", status_code=303, response_class=Response, dependencies=dependencies)
            def create_one_and_redirect_to_get_one_api_with_primary_key(
                    request: Request,
                    insert_args: request_body_model = Depends(),
                    session=Depends(db_session),
            ):

                try:
                    query_result = crud_service.insert_one(insert_args=insert_args, session=session)

                except IntegrityError as e:
                    err_msg, = e.orig.args
                    if 'duplicate key value violates unique constraint' not in err_msg:
                        raise e
                    result = Response(status_code=HTTPStatus.CONFLICT)
                    return result

                return result_parser.post_redirect_get(response_model=response_model,
                                                       sql_execute_result=query_result,
                                                       fastapi_request=request,
                                                       session=session)

    @classmethod
    def patch_one(self, api, *,
                  path,
                  response_model,
                  dependencies,
                  request_url_param_model,
                  request_body_model,
                  request_query_model,
                  db_session,
                  crud_service,
                  result_parser,
                  async_mode):
        if async_mode:
            @api.patch(path,
                       status_code=200,
                       response_model=Union[response_model],
                       dependencies=dependencies)
            async def async_partial_update_one_by_primary_key(
                    response: Response,
                    primary_key: request_url_param_model = Depends(),
                    patch_data: request_body_model = Depends(),
                    extra_query: request_query_model = Depends(),
                    session=Depends(db_session),
            ):
                query_result = await crud_service.async_update(primary_key=primary_key,
                                                               update_args=patch_data,
                                                               extra_query=extra_query,
                                                               session=session)

                return await result_parser.async_patch_one(response_model=response_model,
                                                           sql_execute_result=query_result,
                                                           fastapi_response=response,
                                                           session=session)
        else:
            @api.patch(path,
                       status_code=200,
                       response_model=Union[response_model],
                       dependencies=dependencies)
            def partial_update_one_by_primary_key(
                    response: Response,
                    primary_key: request_url_param_model = Depends(),
                    patch_data: request_body_model = Depends(),
                    extra_query: request_query_model = Depends(),
                    session=Depends(db_session),
            ):
                query_result = crud_service.update(primary_key=primary_key,
                                                   update_args=patch_data,
                                                   extra_query=extra_query,
                                                   session=session)

                return result_parser.patch_one(response_model=response_model,
                                               sql_execute_result=query_result,
                                               fastapi_response=response,
                                               session=session)

    @classmethod
    def patch_many(self, api, *,
                   path,
                   response_model,
                   dependencies,
                   request_body_model,
                   request_query_model,
                   db_session,
                   crud_service,
                   result_parser,
                   async_mode):
        if async_mode:
            @api.patch(path,
                       status_code=200,
                       response_model=response_model,
                       dependencies=dependencies)
            async def async_partial_update_many_by_query(
                    response: Response,
                    patch_data: request_body_model = Depends(),
                    extra_query: request_query_model = Depends(),
                    session=Depends(db_session)
            ):
                query_result = await crud_service.async_update(update_args=patch_data,
                                                               extra_query=extra_query,
                                                               session=session)

                return await result_parser.async_patch_many(response_model=response_model,
                                                            sql_execute_result=query_result,
                                                            fastapi_response=response,
                                                            session=session)
        else:
            @api.patch(path,
                       status_code=200,
                       response_model=response_model,
                       dependencies=dependencies)
            def partial_update_many_by_query(
                    response: Response,
                    patch_data: request_body_model = Depends(),
                    extra_query: request_query_model = Depends(),
                    session=Depends(db_session)
            ):
                query_result = crud_service.update(update_args=patch_data,
                                                   extra_query=extra_query,
                                                   session=session)

                return result_parser.patch_many(response_model=response_model,
                                                sql_execute_result=query_result,
                                                fastapi_response=response,
                                                session=session)

    @classmethod
    def put_one(self, api, *,
                path,
                request_url_param_model,
                request_body_model,
                response_model,
                dependencies,
                request_query_model,
                db_session,
                crud_service,
                result_parser,
                async_mode):
        if async_mode:
            @api.put(path, status_code=200, response_model=response_model, dependencies=dependencies)
            async def async_entire_update_by_primary_key(
                    response: Response,
                    primary_key: request_url_param_model = Depends(),
                    update_data: request_body_model = Depends(),
                    extra_query: request_query_model = Depends(),
                    session=Depends(db_session),
            ):
                query_result = await crud_service.async_update(primary_key=primary_key,
                                                               update_args=update_data,
                                                               extra_query=extra_query,
                                                               session=session)

                return await result_parser.async_update_one(response_model=response_model,
                                                            sql_execute_result=query_result,
                                                            fastapi_response=response,
                                                            session=session)
        else:
            @api.put(path, status_code=200, response_model=response_model, dependencies=dependencies)
            def entire_update_by_primary_key(
                    response: Response,
                    primary_key: request_url_param_model = Depends(),
                    update_data: request_body_model = Depends(),
                    extra_query: request_query_model = Depends(),
                    session=Depends(db_session),
            ):
                query_result = crud_service.update(primary_key=primary_key,
                                                   update_args=update_data,
                                                   extra_query=extra_query,
                                                   session=session)

                return result_parser.update_one(response_model=response_model,
                                                sql_execute_result=query_result,
                                                fastapi_response=response,
                                                session=session)

    @classmethod
    def put_many(self, api, *,
                 path,
                 response_model,
                 dependencies,
                 request_query_model,
                 request_body_model,
                 db_session,
                 crud_service,
                 result_parser,
                 async_mode):
        if async_mode:
            @api.put(path, status_code=200, response_model=response_model, dependencies=dependencies)
            async def async_entire_update_many_by_query(
                    response: Response,
                    update_data: request_body_model = Depends(),
                    extra_query: request_query_model = Depends(),
                    session=Depends(db_session),
            ):
                query_result = await crud_service.async_update(update_args=update_data,
                                                               extra_query=extra_query,
                                                               session=session)

                return await result_parser.async_update_many(response_model=response_model,
                                                             sql_execute_result=query_result,
                                                             fastapi_response=response,
                                                             session=session)
        else:
            @api.put(path, status_code=200, response_model=response_model, dependencies=dependencies)
            async def entire_update_many_by_query(
                    response: Response,
                    update_data: request_body_model = Depends(),
                    extra_query: request_query_model = Depends(),
                    session=Depends(db_session),
            ):
                query_result = crud_service.update(update_args=update_data,
                                                   extra_query=extra_query,
                                                   session=session)

                return result_parser.update_many(response_model=response_model,
                                                 sql_execute_result=query_result,
                                                 fastapi_response=response,
                                                 session=session)
