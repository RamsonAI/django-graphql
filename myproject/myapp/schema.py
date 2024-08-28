import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from graphql_jwt.shortcuts import get_token

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'date_joined')

class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
    
    user = graphene.Field(UserType)
    message = graphene.String()

    def mutate(self, info, username, email, password):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Authorization is required')
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        return CreateUser(user=user, message = 'user created successfully')
    
class ObtainJSONWebToken(graphene.Mutation):
    token = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        user = authenticate(username=username, password=password)

        if user is None:
            raise Exception("Incorrect Username or Password")
        token = get_token(user)
        return ObtainJSONWebToken(token=token, user=user)

class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        username = graphene.String()
        email = graphene.String()

    user = graphene.Field(UserType)

    def mutate(self, info, id, username=None, email=None):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authorization is required")
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            raise Exception("user does not exist")
        
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        
        user.save()
        return UpdateUser(user=user)

class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        username = graphene.String()
        email = graphene.String()

    user = graphene.Field(UserType)

    success = graphene.Boolean()

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authorization is required")
        if not user.is_staff:
            raise Exception("You dot have this permision")
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            raise Exception("User not found")

        user.delete()    
        return DeleteUser(success=True)
    
class UpdatePassword(graphene.Mutation):
    class Arguments:
        current_password = graphene.String(required=True)
        new_password = graphene.String(required=True)

    user = graphene.Field(UserType)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, current_password, new_password):
        user = info.context.user

        if not user.is_authenticated:
            raise Exception("Authorization required")
        
        if not user.check_password(current_password):
            return UpdatePassword(success=False, message=("Current password is incorrect"))
        
        user.set_password(new_password)
        user.save()
        return UpdatePassword(success=True, message=("Password updated successfuly"))

class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)

    def resolve_all_users(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication Required")
        return User.objects.all()

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    delete_user = DeleteUser.Field()
    update_user = UpdateUser.Field()
    login = ObtainJSONWebToken.Field()
    update_password = UpdatePassword.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)