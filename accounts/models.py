from django.core.validators import MinLengthValidator
from django.db import models
from django.conf import settings


def avatar_upload_path(instance, filename):
    return f'avatars/{instance.user.username}/{filename}'


class Contact(models.Model):
    from_profile = models.ForeignKey(
        'Profile',
        related_name='contacts_outgoing',
        on_delete=models.CASCADE,
    )
    to_profile = models.ForeignKey(
        'Profile',
        related_name='contacts_incoming',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ('from_profile', 'to_profile')


class ProjectMember(models.Model):
    member = models.ForeignKey('Profile', on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['member', 'project']


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile',
        on_delete=models.CASCADE,verbose_name='User',)
    avatar = models.ImageField(upload_to=avatar_upload_path,blank=True,
        null=True,verbose_name='Avatar',)
    first_name = models.CharField(max_length=255,
        verbose_name='First Name',)
    last_name = models.CharField(max_length=255,
        verbose_name='Last Name',)
    projects = models.ManyToManyField('Project',
        related_name='profiles',
        blank=True,
        verbose_name='Projects',
    )
    contacts = models.ManyToManyField(
        'self',
        through=Contact,
        through_fields=('from_profile', 'to_profile'),
        verbose_name='Contacts',
    )

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Project(models.Model):
    owner = models.ForeignKey(
        Profile,
        related_name='owned_projects',
        on_delete=models.PROTECT,
        verbose_name='Owner',
    )
    members = models.ManyToManyField(
        Profile,
        through='ProjectMember',
        related_name='joined_projects',
        blank=True,
        verbose_name='Members',

    )
    name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3)],
        verbose_name='Project Name',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description',
    )
    soft_deadline = models.DateTimeField(
        verbose_name='Soft Deadline',
        blank=True,
    )
    deadline = models.DateTimeField(
        verbose_name='Final Deadline',
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At',
    )

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProjectFile(models.Model):
    project = models.ForeignKey(
        Project,
        related_name='files',
        on_delete=models.CASCADE,
        verbose_name='Project',
    )
    file = models.FileField(
        upload_to='project_files/',
        verbose_name='File',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Description',
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Uploaded At',
    )

    class Meta:
        verbose_name = 'Project File'
        verbose_name_plural = 'Project Files'

    def __str__(self):
        return f"File for {self.project.name}"


class Status(models.Model):
    project = models.ForeignKey(
        Project,
        related_name='statuses',
        on_delete=models.CASCADE,
        verbose_name='Project',
    )
    name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3)],
        verbose_name='Status Name',
    )

    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Statuses'

    def __str__(self):
        return self.name


class Task(models.Model):
    status = models.ForeignKey(
        Status,
        related_name='statuses',
        on_delete=models.CASCADE,
        verbose_name='Status',
    )
    creator = models.ForeignKey(
        Profile,
        related_name='created_tasks',
        on_delete=models.DO_NOTHING,
        verbose_name='Creator',
    )
    performer = models.ForeignKey(
        Profile,
        related_name='performed_tasks',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        verbose_name='Performer',
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Task Name',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description',
    )
    soft_deadline = models.DateTimeField(
        verbose_name='Soft Deadline',
    )
    deadline = models.DateTimeField(
        verbose_name='Final Deadline',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At',
    )

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.name


class TaskFile(models.Model):
    task = models.ForeignKey(
        Task,
        related_name='files',
        on_delete=models.CASCADE,
        verbose_name='Task',
    )
    file = models.FileField(
        upload_to='task_files/',
        verbose_name='File',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Description',
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Uploaded At',
    )

    class Meta:
        verbose_name = 'Task File'
        verbose_name_plural = 'Task Files'

    def __str__(self):
        return f"File for {self.task.name}"


class ProjectMessage(models.Model):
    author = models.ForeignKey(
        Profile,
        related_name='project_messages',
        on_delete=models.CASCADE,
        verbose_name='Author',
    )
    project = models.ForeignKey(
        Project,
        related_name='messages',
        on_delete=models.CASCADE,
        verbose_name='Project',
    )
    related_comment = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Related Comment',
    )
    related_file = models.ForeignKey(
        ProjectFile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Related File',
    )
    content = models.TextField(
        blank=False,
        verbose_name='Content',
    )
    time_create = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
    )
    time_update = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At',
    )

    class Meta:
        ordering = ['time_create']
        verbose_name = 'Project Message'
        verbose_name_plural = 'Project Messages'

    def __str__(self):
        return f"Message by {self.author} in {self.project.name}"


class TaskMessage(models.Model):
    author = models.ForeignKey(
        Profile,
        related_name='task_messages',
        on_delete=models.CASCADE,
        verbose_name='Author',
    )
    task = models.ForeignKey(
        Task,
        related_name='messages',
        on_delete=models.CASCADE,
        verbose_name='Task',
    )
    related_comment = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Related Comment',
    )
    related_file = models.ForeignKey(
        TaskFile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Related File',
    )
    content = models.TextField(
        blank=False,
        verbose_name='Content',
    )
    time_create = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
    )
    time_update = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At',
    )

    class Meta:
        ordering = ['time_create']
        verbose_name = 'Task Message'
        verbose_name_plural = 'Task Messages'

    def __str__(self):
        return f"Message by {self.author} in {self.task.name}"