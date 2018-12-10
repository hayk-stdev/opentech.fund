# Generated by Django 2.0.9 on 2018-12-12 17:48

from django.db import migrations, models
import wagtail.core.blocks
import wagtail.core.blocks.static_block
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0014_add_markdown'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='visibility',
            field=models.CharField(choices=[('private', 'Private'), ('reviewers', 'Reviewers and Staff')], default='private', max_length=10, verbose_name='Visibility'),
        ),
        migrations.AlterField(
            model_name='review',
            name='form_fields',
            field=wagtail.core.fields.StreamField([('rich_text', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False)), ('default_value', wagtail.core.blocks.TextBlock(label='Default value', required=False))], group='Fields')), ('markdown_text', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False)), ('default_value', wagtail.core.blocks.TextBlock(label='Default value', required=False))], group='Fields')), ('char', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False)), ('format', wagtail.core.blocks.ChoiceBlock(choices=[('email', 'Email'), ('url', 'URL')], label='Format', required=False)), ('default_value', wagtail.core.blocks.CharBlock(label='Default value', required=False))], group='Fields')), ('text', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False)), ('default_value', wagtail.core.blocks.TextBlock(label='Default value', required=False))], group='Fields')), ('text_markup', wagtail.core.blocks.RichTextBlock(group='Fields', label='Paragraph')), ('score', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False))], group='Fields')), ('checkbox', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False)), ('default_value', wagtail.core.blocks.BooleanBlock(required=False))], group='Fields')), ('dropdown', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False)), ('choices', wagtail.core.blocks.ListBlock(wagtail.core.blocks.CharBlock(label='Choice')))], group='Fields')), ('recommendation', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('info', wagtail.core.blocks.static_block.StaticBlock())], group=' Required')), ('comments', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('info', wagtail.core.blocks.static_block.StaticBlock())], group=' Required')), ('visibility', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('info', wagtail.core.blocks.static_block.StaticBlock())], group=' Required'))]),
        ),
        migrations.AlterField(
            model_name='reviewform',
            name='form_fields',
            field=wagtail.core.fields.StreamField([('rich_text', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False)), ('default_value', wagtail.core.blocks.TextBlock(label='Default value', required=False))], group='Fields')), ('markdown_text', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False)), ('default_value', wagtail.core.blocks.TextBlock(label='Default value', required=False))], group='Fields')), ('char', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False)), ('format', wagtail.core.blocks.ChoiceBlock(choices=[('email', 'Email'), ('url', 'URL')], label='Format', required=False)), ('default_value', wagtail.core.blocks.CharBlock(label='Default value', required=False))], group='Fields')), ('text', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False)), ('default_value', wagtail.core.blocks.TextBlock(label='Default value', required=False))], group='Fields')), ('text_markup', wagtail.core.blocks.RichTextBlock(group='Fields', label='Paragraph')), ('score', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False))], group='Fields')), ('checkbox', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False)), ('default_value', wagtail.core.blocks.BooleanBlock(required=False))], group='Fields')), ('dropdown', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('required', wagtail.core.blocks.BooleanBlock(label='Required', required=False)), ('choices', wagtail.core.blocks.ListBlock(wagtail.core.blocks.CharBlock(label='Choice')))], group='Fields')), ('recommendation', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('info', wagtail.core.blocks.static_block.StaticBlock())], group=' Required')), ('comments', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('info', wagtail.core.blocks.static_block.StaticBlock())], group=' Required')), ('visibility', wagtail.core.blocks.StructBlock([('field_label', wagtail.core.blocks.CharBlock(label='Label')), ('help_text', wagtail.core.blocks.TextBlock(label='Help text', required=False)), ('info', wagtail.core.blocks.static_block.StaticBlock())], group=' Required'))]),
        ),
    ]
