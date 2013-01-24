# Governor

Object-level permissions are very useful, however setting them up and
managing changes can be a big pain in the ass. Governor attempts to
alleviate some of this pain.

The steps for integrating object-level permissions in a project consists
typically of three steps:

- Determine what requires the permission
- Define the scope of the permission and how it integrates in the application
- Determine which users and groups the permission may be granted to

The last step gets hung up on implementation details:

- _Where in my app should I grant this permission? Is it the only entry point?_
- _What happens when content is created and permission needs to be granted?_
- _What happens when a user is created who needs to be assigned permissions?_

Which users/groups should be granted permission is generally determined by
some characteristic, condition, implied relationship, etc. The simplest
example of this is Django's `User.is_superuser` flag. If that is true, the
user has permission to _everything_. Obviously that is a simple example, but
makes the point that permission generally derive from some existing condition.

## How does Governor help?

Governor makes it easy to define isolated conditional logic for determine
which users and groups are _eligible_ for being granted the permission.

Django-guardian is the object-permission backend which provides the models
and various utilies for assigning/removing permissions **once they are
known**.

## Other Notes
Defines the logic surrounding the lifecycle of an object-level
permission.

There are three states that need to handled to ensure consistency
in the application for both the object and user/groups:

1. Initialization
2. Updates
3. Delete

When a new object is created, the relevant users/groups must be linked
up with the new object. If the availability of the permission for the
object is dependent on some other factor (an attribute/other perm), each
time the object (or a related object) is saved, the users/groups must be
updated accordingly. Likewise, when the object is deleted, any bound
permissions to users/groups must be dropped.

When a new user/group is created, all permissions that apply to the user
or group must be synchronized for the relevant objects.

