#!/usr/bin/ruby

require 'vips'

image_extensions = ['.png']

images_dir = File.join(File.dirname(__dir__), 'cards')
assets_dir = File.join(File.dirname(__dir__), 'react-snowpack', 'public')

filenames = Dir.each_child(images_dir)
               .select { |f| image_extensions.include? File.extname(f) }
images = filenames.map { |f| Vips::Image.new_from_file("#{images_dir}/#{f}", access: :sequential) }
image_height = 150
image_width = 240

Vips::Image.arrayjoin(images, across: 3).write_to_file "#{assets_dir}/sprites.png"

stylesheet = ['.card { background-image: url("sprites.png"); }']
filenames.each_with_index do |filename, idx|
  top = idx.div(3) * image_height
  left = idx.remainder(3) * image_width
  stylesheet << ".#{filename.sub! /\..*$/, ''} " '{' " background-position: top #{-top}px left #{-left}px; " '}'
end

File.open("#{assets_dir}/sprites.css", 'w') do |f|
  stylesheet.each { |line| f.write(line << "\n") }
end
