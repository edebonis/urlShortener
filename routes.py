from app import create_app, db
from flask import jsonify, request, redirect
from models import URL

# Creates the Flask app instance
app = create_app()


@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """
    API endpoint to shorten a URL
    Get the URL from the request and add it to the database
    """
    destination_url = request.json['destination_url']
    url = URL(destination_url=destination_url)
    db.session.commit()
    return jsonify({'short_url': url.short_url}), 201


@app.route('/<short_url>', methods=['GET'])
def redirect_to_url(short_url):
    """
    API endpoint to redirect to a URL
    Get the short URL from the request and redirect to the destination URL
    """
    url = URL.query.filter_by(short_url=short_url, enabled=True).first_or_404()
    return redirect(url.destination_url)


@app.route('/api/update/<short_url>', methods=['POST'])
def update_url(short_url):
    """
    API endpoint to update a URL
    Get the short URL from the request and update the destination URL
    """
    url = URL.query.filter_by(short_url=short_url).first_or_404()
    print(url)
    new_url = request.json['destination_url']
    url.destination_url = new_url
    db.session.commit()
    return jsonify({'short_url': url.short_url, 'destination_url': url.destination_url})


@app.route('/api/disable/<short_url>', methods=['POST'])
def disable_url(short_url):
    """
    API endpoint to disable a URL
    Get the short URL from the request and disable the destination URL. Update the flag in the database.
    """
    url = URL.query.filter_by(short_url=short_url).first_or_404()
    url.enabled = False
    db.session.commit()
    return jsonify({'short_url': url.short_url, 'destination_url': url.destination_url})


@app.route('/api/enable/<short_url>', methods=['POST'])
def enable_url(short_url):
    """
    API endpoint to enable a URL
    Get the short URL from the request and enable the destination URL. Update the flag in the database.
    """
    url = URL.query.filter_by(short_url=short_url).first_or_404()
    url.enabled = True
    db.session.commit()
    return jsonify({'short_url': url.short_url, 'destination_url': url.destination_url})
