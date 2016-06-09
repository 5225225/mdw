function mathjax_download {
    curl -OL https://github.com/mathjax/MathJax/archive/master.zip
    unzip master.zip
    mv MathJax-master MathJax
}


mkdir -p files logs wiki

if [ ! -e wiki/homepage.md ]; then
tee wiki/homepage.md << EOF
# Homepage

This is the default homepage.
EOF
fi

echo "How should Mathjax be served?"
echo "Local)    requires a 30MB download and (curl, unzip) to be installed)"
echo "CDN)      loads it from their website"
echo "None)     disables it (Doesn't download at all, it will not execute)"
echo "            Use if you are downloading yourself manually"

select method in "Local" "CDN" "None"; do
    case $method in
        Local)
            mathjax_download
            break
            ;;
        CDN)
            sed -i "s:/MathJax/MathJax.js:https\://cdn.mathjax.org/mathjax/latest/MathJax.js:" \
                templates/base.html
            break
            ;;
        None)
        break
        ;;
    esac
done
