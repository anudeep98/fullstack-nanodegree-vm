"""Defines the views to be presented to the user."""
from flask import render_template, request, redirect, url_for
from sqlalchemy import desc
from sqlalchemy.orm.exc import NoResultFound

from catalog import app, session
from database_setup import Category, Item

# Dummy database for testing the templates
categories = [
    {'id': '1', 'name': 'Mammals'},
    {'id': '2', 'name': 'Birds'},
    {'id': '3', 'name': 'Fish'},
    {'id': '4', 'name': 'Reptiles'},
    {'id': '5', 'name': 'Amphibians'},
    {'id': '6', 'name': 'Arthropods'}
]

category = {'id': '1', 'name': 'Mammals'}

items = [
    {'id': '1', 'name': 'Elephant', 'description': 'Large, grey animal',
     'category_id': '1'},
    {'id': '2', 'name': 'Polar Bear', 'description': 'Large, white animal',
     'category_id': '1'},
    {'id': '3', 'name': 'Kingfisher', 'description': 'Bird that eats fish',
     'category_id': '2'},
    {'id': '4', 'name': 'Blue Tit', 'description': 'A blue & yellow bird',
     'category_id': '2'},
    {'id': '5', 'name': 'Swordfish', 'description': 'Fish with a sword',
     'category_id': '3'},
    {'id': '6', 'name': 'Whale Shark', 'description': 'A big shark',
     'category_id': '3'}
]

item = {'id': '1', 'name': 'Elephant', 'description': 'Large, grey animal',
        'category_id': '1'}


@app.route('/')
@app.route('/catalog/')
def show_homepage():
    """Show the homepage diplaying the categories and latest items."""
    categories = session.query(Category).all()
    latest_items = session.query(Item).order_by(desc(Item.id))[0:10]
    return render_template('homepage.html',
                           categories=categories,
                           latest_items=latest_items)


@app.route('/catalog/<category_name>/items/')
def show_items(category_name):
    """Show items belonging to a specified category."""
    try:
        category = session.query(Category).filter_by(name=category_name).one()
    except NoResultFound:
        # TODO Make this a flash message
        return "The category '%s' does not exist." % category_name

    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category=category).all()
    return render_template('items.html',
                           categories=categories,
                           category=category,
                           items=items)


@app.route('/catalog/<category_name>/<item_name>/')
def show_item(category_name, item_name):
    """Show details of a particular item belonging to a specified category."""
    try:
        category = session.query(Category).filter_by(name=category_name).one()
    except NoResultFound:
        # TODO Make this a flash message on homepage.
        return "The category '%s' does not exist." % category_name

    try:
        item = session.query(Item).filter_by(name=item_name).one()
    except NoResultFound:
        # TODO Make this a flash message on homepage.
        return "The item '%s' does not exist." % item_name

    categories = session.query(Category).all()
    return render_template('item.html',
                           categories=categories,
                           category=category,
                           item=item)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def create_item():
    """Allow users to create a new item in the catalog."""
    if request.method == 'POST':
        if request.form['name'] == "items":
            # Can't have an item called "items" as this is a route.
            # TODO Replace with flash message.
            return "Can't have an item called 'items'."

        category = (session.query(Category)
                    .filter_by(name=request.form['category']).one())
        new_item = Item(category=category,
                        name=request.form['name'],
                        description=request.form['description'])
        session.add(new_item)
        session.commit()
        return redirect(url_for('show_homepage'))
    else:
        categories = session.query(Category).all()
        return render_template('new_item.html',
                               categories=categories)


@app.route('/catalog/<item_name>/edit/', methods=['GET', 'POST'])
def edit_item(item_name):
    """Edit the details of the specified item."""
    try:
        item = session.query(Item).filter_by(name=item_name).one()
    except NoResultFound:
        # TODO Make this a flash message on homepage.
        return "The item '%s' does not exist." % item_name

    if request.method == 'POST':
        form_category = (session.query(Category)
                         .filter_by(name=request.form['category']).one())

        if form_category != item.category:
            item.category = form_category

        if request.form['name']:
            item.name = request.form['name']
        item.description = request.form['description']

        session.add(item)
        session.commit()

        return redirect(url_for('show_items', category_name=form_category.name))
    else:
        categories = session.query(Category).all()
        return render_template('edit_item.html',
                               categories=categories,
                               item=item)


@app.route('/catalog/<item_name>/delete/')
def delete_item(item_name):
    """Delete a specified item from the database."""
    return render_template('delete_item.html',
                           categories=categories,
                           item=item)
