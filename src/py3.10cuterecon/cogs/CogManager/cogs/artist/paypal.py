import discord
import paypalrestsdk
import logging
import json
import inspect
import random
import asyncio
import string
from discord.ext import commands
from discord.utils import get
from redbot.core.utils.chat_formatting import warning, error, info
from paypalrestsdk import Invoice, Payment, ResourceNotFound
from discord import Embed
from redbot.core import commands
from redbot.core import checks
from redbot.core import Config
from redbot.core.data_manager import cog_data_path

#from .init import Init

__author__ = "Teemo the Yiffer"

class Paypal():
    @commands.group(name="paypal")
    async def _paypal(self, ctx):
        """
        Teemo's PayPal invoicing service.
        """

    @_paypal.command(name="pay")
    async def _pay(self, ctx):
        """
        [Setup Required] Pay anyone with only their e-mail.
        """
        try:
            logging.basicConfig(level=logging.INFO)
            paypalrestsdk.configure({
                "mode": "live", # sandbox or live
                "client_id": await self.artist.get_raw(ctx.message.author.id,"Paypal_clientid"),
                "client_secret": await self.artist.get_raw(ctx.message.author.id,'Paypal_secret')})
        except StopIteration:
            await ctx.send("You're not in the database. If you're interested in being added, type '>contact' to notify Teemo the Yiffer.", delete_after=100)
            return

        await ctx.send("Regarding the person you're sending money to, What's their PayPal e-mail?")
        Email = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        await ctx.send("What's the amount you want to send? Just numbers please!")
        Cost = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        await ctx.send("What currency is the money? Enter your currency code. For example: USD, CAD, EUR, etc.")
        Currency = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        author = ctx.message.author
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            'redirect_urls':{
                'return_url':'http://184.105.151.182/process.html',
                'cancel_url':'http://184.105.151.182/cancel.html'
                },
            "payer": {
                "payment_method": "paypal"},
            "transactions": [{
                "amount": {
                    "total": Cost.content,
                    "currency": Currency.content
                    },
                'payee':{
                    'email': Email.content
                },
                "description": "This payment was sent by %s from Discord with Teemo the Yiffer's bot!" % author}]})

        if payment.create():
            await ctx.send("Payment[%s] created successfully" % (payment.id))
            for link in payment.links:
                if link.method == "REDIRECT":
                    redirect_url = str(link.href)
                    await ctx.send("Redirect for approval: %s" % (redirect_url))
            await ctx.send("You have two minutes to approve the purchase via the link above.")

            await asyncio.sleep(60)

            try:
                payment = paypalrestsdk.Payment.find(payment.id)
                payerid = payment.payer.payer_info.payer_id
                if payment.execute({"payer_id": payerid}):
                    await ctx.send("Payment[%s] was approved and executed." % (payment.id))
            except:
                await ctx.send("Payment Timeout. Try again.")
                return
        else:
            await ctx.send(payment.error)
            return

    @_paypal.command(name="artist")
    async def _paypalartist(self, ctx, *, artist):
        """
        [Setup Required] Pay any artist from !artists list.
        """
        a = await self.artist.all()
        try:
            artistid = next(k for k, v in a.items() if ("Name", artist) in v.items())
        except StopIteration:
            await ctx.send("Sorry but that artist is not in the database or the name was incorrect. Check the artist list by running: >artists")
            return

        try:
            logging.basicConfig(level=logging.INFO)
            paypalrestsdk.configure({
                "mode": "live", # sandbox or live
                "client_id": await self.artist.get_raw(ctx.message.author.id,"Paypal_clientid"),
                "client_secret": await self.artist.get_raw(ctx.message.author.id,'Paypal_secret')})
        except StopIteration:
            await ctx.send("You're not in the database. If you're interested in being added, type '>contact' to notify Teemo the Yiffer.", delete_after=100)
            return
        
        Email = await self.artist.get_raw(artistid,"Paypal_email")
        await ctx.send("What's the amount you want to send? Just numbers please!")
        Cost = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        await ctx.send("What currency is the money? Enter your currency code. For example: USD, CAD, EUR, etc.")
        Currency = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        author = ctx.message.author
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            'redirect_urls':{
                'return_url':'http://35.235.68.102/process.html',
                'cancel_url':'http://35.235.68.102/cancel.html'
                },
            "payer": {
                "payment_method": "paypal"},
            "transactions": [{
                "amount": {
                    "total": Cost.content,
                    "currency": Currency.content
                    },
                'payee':{
                    'email': Email
                },
                "description": "This payment was sent by %s from Discord with Teemo the Yiffer's bot!" % author}]})

        if payment.create():
            await ctx.send("Payment[%s] created successfully" % (payment.id))
            for link in payment.links:
                if link.method == "REDIRECT":
                    redirect_url = str(link.href)
                    await ctx.send("Redirect for approval: %s" % (redirect_url))
            await ctx.send("You have two minutes to approve the purchase via the link above.")

            await asyncio.sleep(60)

            try:
                payment = paypalrestsdk.Payment.find(payment.id)
                payerid = payment.payer.payer_info.payer_id
                if payment.execute({"payer_id": payerid}):
                    await ctx.send("Payment[%s] was approved and executed." % (payment.id))
            except:
                await ctx.send("Payment Timeout. Try again.")
                return
        else:
            await ctx.send(payment.error)
            return

    @_paypal.command(name="invoice")
    async def _invoice(self, ctx):
        """
        [Setup Required] Invoice anyone with only their e-mail.
        """
        try:
            all(self.artist[ctx.message.author.id]['embed']['author'][x] for x in ['paypal.client_id', 'paypal.secret'])
        except:
            await ctx.send("You're not in the database. If you're interested in being added, type '>contact' to notify Teemo the Yiffer.")
            return
        logging.basicConfig(level=logging.INFO)
        paypalrestsdk.configure({
            "mode": "live", # sandbox or live
            "client_id": self.artist[ctx.message.author.id]['embed']['author']['paypal.client_id'],
            "client_secret": self.artist[ctx.message.author.id]['embed']['author']['paypal.secret'] })

        await ctx.send("Please state the new customer's e-mail you wish to add.")
        CustomerEmail = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        await ctx.send("How much we charging? Just numbers please!")
        Cost = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        await ctx.send("What currency we charging them with? Enter your currency code. For example: USD, CAD, EUR, etc.")
        Currency = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        invoice = Invoice({
            "note": "Thank you for your support!",
            "logo_url": ctx.message.author.avatar_url,
            "merchant_info": {
                "email": self.artist[ctx.message.author.id]['embed']['author']['paypal.email'], 
            },
            "billing_info": [{"email": CustomerEmail.content}],
            "items": [
                {
                    "name": "Commission",
                    "quantity": 1,
                    "unit_price": {
                        "currency": Currency.content,
                        "value": Cost.content
                    }
                }
            ],
            "payment_term": {
                "term_type": "NET_10"
            }
        })

        if invoice.create():
            InvoiceID = invoice['id']
            if invoice.send():  # return True or False
                await ctx.send("Invoice for %s was created & sent!" % CustomerEmail.content)
            else:
                await ctx.send(invoice.error)
            await ctx.send("Be sure to keep track of your invoice ID to check it's status! Invoice ID: %s" % InvoiceID)
            await ctx.send("Pay here: https://www.sandbox.paypal.com/invoice/details/%s" % InvoiceID)
            try:
                dump = json.dumps(invoice.to_dict(), sort_keys=False, indent=4)
                await ctx.send(dump)
            except:
                return
        else:
            await ctx.send(invoice.error)
            return

    @_paypal.command(name="check")
    async def _check(self, ctx, *, arg):
        """
        Check a PayPal invoice with invoice ID.
        Command: >paypal check [invoice_ID]
        """
        logging.basicConfig(level=logging.INFO)
        paypalrestsdk.configure({
            "mode": "live", # sandbox or live
            "client_id": self.artist[ctx.message.author.id]['embed']['author']['paypal.client_id'],
            "client_secret": self.artist[ctx.message.author.id]['embed']['author']['paypal.secret'] })
        try:
            invoice = Invoice.find(arg)
            invoicestatus = invoice['status']
            await ctx.send("Status: ` %s `" % invoicestatus)
        except:
            return ctx.send("Invoice not found!")
        
    @_paypal.command(name="cancel")
    async def _cancel(self, ctx, *, arg):
        """
        Cancel a PayPal invoice with invoice ID.
        Command: >paypal cancel [invoice_ID]
        """
        logging.basicConfig(level=logging.INFO)
        paypalrestsdk.configure({
            "mode": "live", # sandbox or live
            "client_id": self.artist[ctx.message.author.id]['embed']['author']['paypal.client_id'],
            "client_secret": self.artist[ctx.message.author.id]['embed']['author']['paypal.secret'] })
        try:
            invoice = Invoice.find(arg)
            options = {
                "subject": "Past due",
                "note": "Canceling invoice",
                "send_to_merchant": True,
                "send_to_payer": True
            }
            invoice.cancel(options)
            invoicestatus = invoice['status']
            await ctx.send("I went ahead and cancelled your invoice.")
            await ctx.send("Status: ` %s `" % invoicestatus)
        except:
            return ctx.send("Invoice not found!")

    @_paypal.command(name="remind")
    async def _remind(self, ctx, *, arg):
        """
        Remind a buyer of a pending PayPal invoice with invoice ID.
        Command: >paypal remind [invoice_ID]
        """
        logging.basicConfig(level=logging.INFO)
        paypalrestsdk.configure({
            "mode": "live", # sandbox or live
            "client_id": self.artist[ctx.message.author.id]['embed']['author']['paypal.client_id'],
            "client_secret": self.artist[ctx.message.author.id]['embed']['author']['paypal.secret'] })
        try:
            invoice = Invoice.find(arg)
            options = options = {
                "subject": "Past due",
                "note": "Please pay soon",
                "send_to_merchant": True
            }
            invoice.remind(options)
            invoicestatus = invoice['status']
            await ctx.send("Reminder sent!")
            await ctx.send("Status: ` %s `" % invoicestatus)
        except:
            return ctx.send("Invoice not found!")

    @commands.group(name="stripe")
    async def _stripe(self, ctx):
        """
        Stripe testing ground.
        """

    @_stripe.command(name="add")
    async def _addcustomer(self, ctx):
        """
        Stripe testing ground.
        """
        stripe.api_key = self.artist[ctx.message.author.id]['embed']['author']['stripe.api_key']
        await ctx.send("Please state the new customer's e-mail you wish to add.")
        CustomerEmail = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        stripe.Customer.create(
            email=CustomerEmail.content,
            description='Added from Discord'
            )
        try:
            customer = stripe.Customer.list(email=CustomerEmail.content)
            await ctx.send("%s was added!" % CustomerEmail.content)
        except:
            await ctx.send("Oh no! I failed to add the customer to your Stripe account! I've notified Teemo the Yiffer.")
            self.Reason = "Artist embed creation failure."
            await self.report(ctx)
            return
        CustomerID = customer['data'][0]['id']
        await ctx.send("How much we charging? Just numbers please!")
        Cost = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        await ctx.send("What currency we charging them with? Enter your currency code. For example: USD, CAD, EUR, etc.")
        Currency = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        stripe.InvoiceItem.create(
            amount=Cost.content,
            currency=Currency.content,
            customer=CustomerID,
            description='A commission from discord',
            )
        stripe.Invoice.create(
            customer=CustomerID,
            billing='send_invoice',
            days_until_due=1,
            )
        await ctx.send("Invoice sent!")

    @_stripe.command(name="charge")
    async def _chargecustomer(self, ctx):
        """
        Stripe check
        """
        stripe.api_key = self.artist[ctx.message.author.id]['embed']['author']['stripe.api_key']
        await ctx.send("Customer's e-mail?")
        CustomerEmail = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        try:
            customer = stripe.Customer.list(email=CustomerEmail.content)
            await ctx.send(customer['data'][0])
        except:
            await ctx.send("Oh no! I failed to add the customer to your Stripe account! I've notified Teemo the Yiffer.")
            self.Reason = "Stripe customer addition failure."
            await self.report(ctx)
            return

    @_stripe.command(name="check")
    async def _checkcustomer(self, ctx):
        """
        Stripe check
        """
        stripe.api_key = self.artist[ctx.message.author.id]['embed']['author']['stripe.api_key']
        await ctx.send("Customer's e-mail?")
        CustomerEmail = await self.bot.wait_for('message', timeout=600, check=lambda message: message.author == ctx.author)
        try:
            customer = stripe.Customer.list(email=CustomerEmail.content)
            await ctx.send(customer['data'][0])
        except:
            await ctx.send("Oh no! I failed to add the customer to your Stripe account! I've notified Teemo the Yiffer.")
            self.Reason = "Stripe customer addition failure."
            await self.report(ctx)
            return

    @_stripe.command(name="products")
    async def _products(self, ctx):
        """
        Stripe products
        """
        stripe.api_key = self.artist[ctx.message.author.id]['embed']['author']['stripe.api_key']
        products = stripe.Product.list(limit=50)
        for value in products['data']:
            names = value['name']
            await ctx.send(names)
        for value in products['data']:
            images = value['images']
            await ctx.send(images)